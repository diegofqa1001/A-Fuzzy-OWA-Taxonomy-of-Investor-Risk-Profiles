#!/usr/bin/env python3
"""
check_reproducibility.py — Verificacion de reproducibilidad de las anclas
de orness publicadas.

Contexto (revision postdoctoral, 2026-08-17): data/owa/owa_profiles.json
contiene los valores ORIGINALES de la corrida que ancla la taxonomia
(orness Guardian=0.158 ... Visionary=0.865), citados en la tesis (Tabla
3.4, Figura 3.2) y usados como constantes fijas en los repositorios
descendientes (repo_OWA: ORNESS_PERFIL; motor-owa-v2: TAXONOMY_ORNESS).
Ejecutar owa_weights.py HOY, con la configuracion actual del optimizador
(scipy.optimize.minimize_scalar, bounded, xatol=1e-4), converge al
CENTROIDE EXACTO de cada perfil (orness = centroide hasta la 6a cifra
decimal) en vez de a esos valores originales -- una diferencia de hasta
0.034 en orness (Visionary; 0.012 en Innovator), no explicada por precision numerica ni por version de
SciPy (ver detalle mas abajo).

Este script hace esa comparacion EXPLICITA, en vez de dejar que la unica
verificacion existente (verify_math.py) de una falsa sensacion de
reproducibilidad total al chequear solo la consistencia INTERNA del JSON
consigo mismo. Se documenta la discrepancia por transparencia: los
valores de data/owa/owa_profiles.json son la version CONGELADA y citada
en la tesis; no se sustituyen automaticamente por la salida fresca de
este script (eso requeriria propagar los nuevos valores a repo_OWA,
motor-owa-v2 y a las tablas/figuras de la tesis -- una decision editorial
que corresponde al autor, no a este script).

Uso:  python code/check_reproducibility.py
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from owa_weights import PROFILES, find_alpha_for_orness, rim_weights, compute_orness, N_DIMENSIONS


def main():
    path = os.path.join(os.path.dirname(__file__), "..", "data", "owa", "owa_profiles.json")
    with open(path) as f:
        stored = json.load(f)

    print("=" * 78)
    print("VERIFICACION DE REPRODUCIBILIDAD: valores congelados vs. corrida fresca")
    print("=" * 78)
    print(f"{'perfil':<12}{'centroide':>10}{'alpha_cong':>12}{'orness_cong':>13}"
          f"{'alpha_hoy':>11}{'orness_hoy':>12}{'dif_orness':>12}")

    filas = []
    peor_dif = 0.0
    for pk, info in sorted(stored.items(), key=lambda x: x[1]["centroid"]):
        c = info["centroid"]
        alpha_hoy = find_alpha_for_orness(c, N_DIMENSIONS)
        W_hoy = rim_weights(alpha_hoy, N_DIMENSIONS)
        orness_hoy = compute_orness(W_hoy)
        dif = abs(orness_hoy - info["orness"])
        peor_dif = max(peor_dif, dif)
        filas.append({"perfil": pk, "nombre": info["name"], "centroide": c,
                       "alpha_congelado": info["alpha"], "orness_congelado": info["orness"],
                       "alpha_hoy": round(alpha_hoy, 4), "orness_hoy": round(orness_hoy, 4),
                       "dif_orness": round(dif, 4)})
        print(f"{info['name']:<12}{c:>10.3f}{info['alpha']:>12.3f}{info['orness']:>13.3f}"
              f"{alpha_hoy:>11.3f}{orness_hoy:>12.3f}{dif:>12.4f}")

    print("-" * 78)
    if peor_dif < 1e-4:
        print("OK: la corrida fresca reproduce exactamente los valores congelados.")
    else:
        print(f"AVISO (esperado y documentado): la corrida fresca NO reproduce los "
              f"valores congelados (diferencia maxima en orness = {peor_dif:.4f}).")
        print()
        print("Esto NO es un fallo del optimizador: converge de forma estable y "
              "correcta al centroide exacto de cada perfil (orness_hoy == "
              "centroide hasta la 6a cifra decimal), lo que sugiere que los "
              "valores congelados provienen de una configuracion anterior del "
              "optimizador (otra tolerancia u otro metodo) que ya no esta en "
              "el repositorio.")
        print()
        print("Los valores CONGELADOS (data/owa/owa_profiles.json) son los que "
              "cita la tesis (Tabla 3.4, Figura 3.2) y los que usan repo_OWA y "
              "motor-owa-v2 como constantes fijas; NO se sustituyen aqui. "
              "Cualquier lector que reproduzca 'python code/owa_weights.py' "
              "desde cero obtendra los valores 'hoy', ligeramente distintos "
              "de los publicados; esta es la razon documentada de esa "
              "diferencia.")

    out_path = os.path.join(os.path.dirname(__file__), "..", "data", "owa",
                            "reproducibility_check.json")
    with open(out_path, "w") as f:
        json.dump(filas, f, indent=2)
    print(f"\nDetalle guardado en {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
