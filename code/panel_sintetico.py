#!/usr/bin/env python3
"""
panel_sintetico.py — Pre-validación computacional con panel sintético de agentes
(tesis doctoral, Cap. 3 §3.5.2 y Anexo A). SIMULACIÓN: no es juicio experto humano.

Qué hace (todo con semilla maestra 2026):

  1. Corrida de referencia: lee la matriz archivada de 65 ítems x 12 agentes
     (data/delphi/raw_section_{A,B,C}.csv) y aplica las reglas de decisión del
     Anexo A.5 (mediana >= 4 y CVR de Lawshe >= 0,78 -> «validado con ajustes
     menores»; mediana >= 4 y CVR < 0,78 -> «segunda ronda»; mediana < 4 ->
     «revisión mayor»). Calcula la W de Kendall sobre los 65 ítems con y sin
     corrección por empates (Schmidt, 1997) y la razón W_obs/W_max de Meijering
     et al. (2013) con W_max = 1 - sum_j T_j / [m (n^3 - n)], cota superior de la
     W sin corregir dada la estructura de empates de cada agente (la razón
     coincide algebraicamente con la W corregida). Reporta también la W sobre 20
     objetos (7 dimensiones + 8 perfiles + 5 ítems globales, media de criterios)
     y sin corrección, que es la especificación de data/delphi/results.json.

  2. Modelo generativo de agentes ajustado a la matriz de referencia: cada
     calificación es la discretización de una latente normal
         y_ei = mu_i + b_e + sigma_e * kappa^{o_ei} * z,
     con umbrales fijos 1,5; 2,5; 3,5; 4,5 (escala Likert 1-5). mu_i: nivel del
     ítem; b_e: severidad/aquiescencia del agente; sigma_e: inconsistencia del
     agente; kappa: inflación de la incertidumbre cuando el ítem cae fuera del
     dominio del subpanel (o_ei = 1). Ítems técnicos (dominio del subpanel
     metodológico B): C4, C5 y el criterio «coherencia interna» de los ocho
     perfiles; el resto es dominio del subpanel de contenido A. Estimación por
     máximo a posteriori con previas débiles (declaradas abajo).

  3. Análisis de sensibilidad de 1.000 réplicas:
       R1: N = 12 (6 + 6), agentes nuevos por réplica;
       R2: N ~ U{8,...,16} y composición n_A ~ U{ceil(0,3N),...,floor(0,7N)};
       R3: tamaño de panel N = 8,...,16 (1.000 réplicas por N, subpaneles balanceados).
     Los parámetros de los agentes nuevos se extraen de la distribución ajustada
     (media por subpanel, dispersión combinada). Se reportan media y percentiles
     2,5-97,5 de la tasa de consenso, W corregida y la probabilidad de consenso
     por ítem (ítems frágiles: probabilidad < 0,5 en R1).

Salida: data/delphi/panel_sintetico_resultados.json
Uso:    OMP_NUM_THREADS=1 python code/panel_sintetico.py
"""
from __future__ import annotations

import json
import math
import os
import sys

import numpy as np
import pandas as pd
from scipy import stats
from scipy.optimize import minimize

SEMILLA = 2026
N_REPLICAS = 1000
CVR_UMBRAL = 0.78
MEDIANA_UMBRAL = 4
DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "delphi")
TAU = np.array([-np.inf, 1.5, 2.5, 3.5, 4.5, np.inf])

# Previas débiles del ajuste MAP
PRIOR_MU = (4.3, 1.0)          # nivel del ítem
PRIOR_B = (0.0, 0.5)           # severidad/aquiescencia del agente
PRIOR_LOGSIG = (math.log(0.6), 0.5)
PRIOR_LOGKAPPA = (0.0, 0.5)


# ----------------------------------------------------------------- datos
def cargar():
    filas = []
    for s in "ABC":
        d = pd.read_csv(os.path.join(DATA, f"raw_section_{s}.csv"))
        d["seccion"] = s
        d["clave"] = s + ":" + d["item"] + ":" + d["criterion"]
        filas.append(d)
    D = pd.concat(filas, ignore_index=True)
    orden = list(dict.fromkeys(D["clave"]))
    M = D.pivot_table(index="clave", columns="expert", values="score", aggfunc="first").loc[orden]
    sub = D.drop_duplicates("expert").set_index("expert")["subpanel"].loc[M.columns].to_numpy()
    tecnico = np.array([(k.startswith("C:C4") or k.startswith("C:C5") or k.endswith("Internal Coherence"))
                        for k in M.index])
    return D, M, sub, tecnico


# ----------------------------------------------------------------- estadísticos
def decisiones(X: np.ndarray):
    n, m = X.shape
    med = np.median(X, axis=1)
    ne = (X >= 4).sum(axis=1)
    cvr = (ne - m / 2) / (m / 2)
    val = (med >= MEDIANA_UMBRAL) & (cvr >= CVR_UMBRAL - 1e-12)
    seg = (med >= MEDIANA_UMBRAL) & ~val
    may = med < MEDIANA_UMBRAL
    return val, seg, may, med, cvr


def kendall_w(X: np.ndarray):
    """W de Kendall (objetos = filas, jueces = columnas), con y sin corrección por empates."""
    n, m = X.shape
    R = np.apply_along_axis(stats.rankdata, 0, X)
    Rs = R.sum(axis=1)
    S = float(((Rs - Rs.mean()) ** 2).sum())
    T = 0.0
    for j in range(m):
        _, t = np.unique(X[:, j], return_counts=True)
        T += float((t ** 3 - t).sum())
    base = m * m * (n ** 3 - n)
    w_sin = 12 * S / base
    den = base - m * T
    w_cor = 12 * S / den if den > 0 else float("nan")
    chi2 = m * (n - 1) * w_cor
    p = float(stats.chi2.sf(chi2, n - 1))
    w_max = 1 - T / (m * (n ** 3 - n))
    return {"W_sin_correccion": w_sin, "W_corregida": w_cor, "chi2": chi2, "gl": n - 1, "p": p,
            "W_max_sin_correccion": w_max, "razon_Wobs_Wmax": w_sin / w_max if w_max > 0 else float("nan")}


# ----------------------------------------------------------------- modelo
def neg_log_post(theta, X, o, n, m):
    mu = theta[:n]
    b = theta[n:n + m]
    logsig = theta[n + m:n + 2 * m]
    logk = theta[-1]
    sd = np.exp(logsig)[None, :] * np.exp(logk * o)
    loc = mu[:, None] + b[None, :]
    xi = X.astype(int)
    hi = (TAU[xi] - loc) / sd
    lo = (TAU[xi - 1] - loc) / sd
    pr = np.clip(stats.norm.cdf(hi) - stats.norm.cdf(lo), 1e-300, None)
    ll = np.log(pr).sum()
    lp = (-0.5 * ((mu - PRIOR_MU[0]) / PRIOR_MU[1]) ** 2).sum() \
        + (-0.5 * ((b - PRIOR_B[0]) / PRIOR_B[1]) ** 2).sum() \
        + (-0.5 * ((logsig - PRIOR_LOGSIG[0]) / PRIOR_LOGSIG[1]) ** 2).sum() \
        + (-0.5 * ((logk - PRIOR_LOGKAPPA[0]) / PRIOR_LOGKAPPA[1]) ** 2)
    return -(ll + lp)


def ajustar(X, sub, tecnico):
    n, m = X.shape
    # o_ei = 1 si el ítem cae fuera del dominio del agente
    o = np.where(sub[None, :] == "B", (~tecnico)[:, None], tecnico[:, None]).astype(float)
    theta0 = np.concatenate([X.mean(axis=1), X.mean(axis=0) - X.mean(), np.full(m, math.log(0.6)), [0.0]])
    res = minimize(neg_log_post, theta0, args=(X, o, n, m), method="L-BFGS-B",
                   options={"maxiter": 5000, "maxfun": 500000})
    th = res.x
    return {"mu": th[:n], "b": th[n:n + m], "sigma": np.exp(th[n + m:n + 2 * m]),
            "kappa": float(math.exp(th[-1])), "convergencia": bool(res.success), "o": o,
            "nlp": float(res.fun)}


def simular(rng, mu, tecnico, nA, nB, dist):
    """Panel sintético nuevo con nA agentes de contenido y nB metodológicos."""
    subs = np.array(["A"] * nA + ["B"] * nB)
    b = np.where(subs == "A", rng.normal(dist["bA"], dist["sd_b"], len(subs)),
                 rng.normal(dist["bB"], dist["sd_b"], len(subs)))
    ls = np.where(subs == "A", rng.normal(dist["lsA"], dist["sd_ls"], len(subs)),
                  rng.normal(dist["lsB"], dist["sd_ls"], len(subs)))
    o = np.where(subs[None, :] == "B", (~tecnico)[:, None], tecnico[:, None]).astype(float)
    sd = np.exp(ls)[None, :] * dist["kappa"] ** o
    y = mu[:, None] + b[None, :] + sd * rng.standard_normal((len(mu), len(subs)))
    return np.clip(np.floor(y + 0.5), 1, 5)


def resumen(v):
    v = np.asarray(v, float)
    return {"media": float(v.mean()), "p2_5": float(np.percentile(v, 2.5)),
            "p97_5": float(np.percentile(v, 97.5)), "min": float(v.min()), "max": float(v.max())}


# ----------------------------------------------------------------- principal
def main() -> int:
    D, M, sub, tecnico = cargar()
    X = M.to_numpy(float)
    n, m = X.shape
    out = {"semilla": SEMILLA, "n_items": n, "n_agentes": m, "estatus": "simulación (panel sintético)"}

    # 1. corrida de referencia
    val, seg, may, med, cvr = decisiones(X)
    kw = kendall_w(X)
    Dm = D.assign(obj=D["seccion"] + ":" + D["item"])
    M20 = Dm.pivot_table(index="obj", columns="expert", values="score", aggfunc="mean").to_numpy(float)
    kw20 = kendall_w(M20)
    out["referencia"] = {
        "validados": int(val.sum()), "segunda_ronda": int(seg.sum()), "revision_mayor": int(may.sum()),
        "tasa_consenso": float(val.mean()),
        "items_segunda_ronda": [k for k, s in zip(M.index, seg) if s],
        "kendall_65_items": kw,
        "kendall_20_objetos": {"W_sin_correccion": kw20["W_sin_correccion"], "gl": kw20["gl"],
                                "W_corregida": kw20["W_corregida"], "p_corregida": kw20["p"]},
        "por_seccion": {s: kendall_w(X[[k.startswith(s + ":") for k in M.index]]) for s in "ABC"},
    }

    # 2. ajuste del modelo generativo
    fit = ajustar(X, sub, tecnico)
    bA, bB = fit["b"][sub == "A"], fit["b"][sub == "B"]
    lsA, lsB = np.log(fit["sigma"][sub == "A"]), np.log(fit["sigma"][sub == "B"])
    dist = {"bA": float(bA.mean()), "bB": float(bB.mean()),
            "sd_b": float(np.sqrt((bA.var(ddof=1) + bB.var(ddof=1)) / 2)),
            "lsA": float(lsA.mean()), "lsB": float(lsB.mean()),
            "sd_ls": float(np.sqrt((lsA.var(ddof=1) + lsB.var(ddof=1)) / 2)),
            "kappa": fit["kappa"]}
    out["modelo"] = {"convergencia": fit["convergencia"], "kappa_fuera_de_dominio": fit["kappa"],
                     "items_tecnicos": [k for k, t in zip(M.index, tecnico) if t],
                     "agentes": {e: {"subpanel": s, "b": float(bb), "sigma": float(sg)}
                                 for e, s, bb, sg in zip(M.columns, sub, fit["b"], fit["sigma"])},
                     "distribucion_agentes": dist,
                     "mu_items": {k: float(v) for k, v in zip(M.index, fit["mu"])},
                     "previas": {"mu": PRIOR_MU, "b": PRIOR_B, "log_sigma": PRIOR_LOGSIG,
                                 "log_kappa": PRIOR_LOGKAPPA}}

    ss = np.random.SeedSequence(SEMILLA)
    hijos = ss.spawn(3)

    # verificación: agentes ajustados fijos, nuevo ruido
    rngv = np.random.default_rng(hijos[0])
    tasas_v = []
    for _ in range(N_REPLICAS):
        sd = fit["sigma"][None, :] * fit["kappa"] ** fit["o"]
        y = fit["mu"][:, None] + fit["b"][None, :] + sd * rngv.standard_normal((n, m))
        Xs = np.clip(np.floor(y + 0.5), 1, 5)
        tasas_v.append(decisiones(Xs)[0].mean())
    out["verificacion_modelo_agentes_ajustados"] = resumen(tasas_v)

    # 3. réplicas
    rng1, rng2 = [np.random.default_rng(h) for h in hijos[1].spawn(2)]
    r1, w1, p1, prob_item = [], [], [], np.zeros(n)
    for _ in range(N_REPLICAS):
        Xs = simular(rng1, fit["mu"], tecnico, 6, 6, dist)
        v = decisiones(Xs)[0]
        r1.append(v.mean())
        prob_item += v
        k = kendall_w(Xs)
        w1.append(k["W_corregida"])
        p1.append(k["p"])
    prob_item /= N_REPLICAS
    fragiles = [(k, float(p)) for k, p in zip(M.index, prob_item) if p < 0.5]
    out["R1_N12"] = {"tasa_consenso": resumen(r1), "W_corregida": resumen(w1),
                     "fraccion_p_menor_0_001": float(np.mean(np.array(p1) < 0.001)),
                     "items_fragiles_prob_menor_0_5": fragiles,
                     "n_items_fragiles": len(fragiles),
                     "prob_consenso_items_segunda_ronda_referencia":
                         {k: float(p) for k, p in zip(M.index, prob_item) if k in out["referencia"]["items_segunda_ronda"]}}

    r2, n2 = [], []
    for _ in range(N_REPLICAS):
        N = int(rng2.integers(8, 17))
        nA = int(rng2.integers(math.ceil(0.3 * N), math.floor(0.7 * N) + 1))
        Xs = simular(rng2, fit["mu"], tecnico, nA, N - nA, dist)
        r2.append(decisiones(Xs)[0].mean())
        n2.append(N)
    out["R2_N_variable"] = {"tasa_consenso": resumen(r2)}

    tam = {}
    for N, h in zip(range(8, 17), hijos[2].spawn(9)):
        rng = np.random.default_rng(h)
        tasas = [decisiones(simular(rng, fit["mu"], tecnico, N // 2, N - N // 2, dist))[0].mean()
                 for _ in range(N_REPLICAS)]
        ne_min = math.ceil((CVR_UMBRAL + 1) * N / 2 - 1e-12)
        tam[str(N)] = {"tasa_media": float(np.mean(tasas)), "p2_5": float(np.percentile(tasas, 2.5)),
                       "p97_5": float(np.percentile(tasas, 97.5)),
                       "acuerdo_minimo_exigido": f"{ne_min}/{N}", "proporcion_minima": ne_min / N}
    out["R3_tamano_panel"] = tam
    out["R3_N_con_tasa_maxima"] = max(tam, key=lambda k: tam[k]["tasa_media"])

    ruta = os.path.join(DATA, "panel_sintetico_resultados.json")
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)

    # consola
    ref = out["referencia"]
    print(f"Referencia: {ref['validados']}/{n} validados, {ref['segunda_ronda']} segunda ronda, "
          f"{ref['revision_mayor']} revisión mayor")
    print("  segunda ronda:", ref["items_segunda_ronda"])
    print("  W 65 ítems:", {k: round(v, 4) if isinstance(v, float) else v for k, v in kw.items()})
    print("  W 20 objetos sin corrección:", round(kw20["W_sin_correccion"], 4))
    print("Modelo: kappa =", round(fit["kappa"], 3), "conv =", fit["convergencia"], dist)
    print("Verificación (agentes ajustados):", out["verificacion_modelo_agentes_ajustados"])
    print("R1 N=12:", out["R1_N12"]["tasa_consenso"], "W:", out["R1_N12"]["W_corregida"],
          "p<0,001:", out["R1_N12"]["fraccion_p_menor_0_001"])
    print("  frágiles:", fragiles)
    print("  prob. ítems 2.ª ronda ref.:", out["R1_N12"]["prob_consenso_items_segunda_ronda_referencia"])
    print("R2 N var:", out["R2_N_variable"])
    for N, v in tam.items():
        print(f"  N={N}: {v['tasa_media']:.3f} [{v['p2_5']:.3f}, {v['p97_5']:.3f}] exige {v['acuerdo_minimo_exigido']}")
    print("->", ruta)
    return 0


if __name__ == "__main__":
    sys.exit(main())
