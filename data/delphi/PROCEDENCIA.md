# Procedencia de los datos del panel (`data/delphi/`)

Todos los archivos de esta carpeta corresponden a un **panel sintético de doce
agentes** (E01–E12) usado como pre-validación computacional del protocolo de
validación de contenido (tesis, §3.5.2 y Anexo A). **Ningún experto humano
participó en su generación.** La ronda con expertos humanos está pendiente del
aval del comité de ética institucional y sus datos no están en este repositorio.

| Archivo | Qué es | Cómo se obtiene |
|---|---|---|
| `raw_section_A.csv`, `raw_section_B.csv`, `raw_section_C.csv` | Matriz de referencia de calificaciones Likert 1–5 (65 ítems × 12 agentes) | Insumo archivado: calificaciones generadas para agentes sintéticos, sin intervención humana. Ningún script de este repositorio las genera; `code/panel_sintetico.py` las **lee** y ajusta sobre ellas el modelo generativo de las réplicas. |
| `expert_panel.csv` | Composición del panel | Subpanel (A contenido, B metodológico) y especialidad son atributos **simulados** asignados a cada agente; `years` y `gender` no aplican (agentes simulados); sin afiliación institucional (`tipo = agente_sintetico`). |
| `qualitative.json` | Observaciones textuales por ítem | Texto generado para los agentes sintéticos; no son comentarios de personas (clave `_procedencia`). |
| `results.json`, `decisions.json` | Estadísticos y decisiones de la corrida de referencia | `code/delphi_analysis.py` sobre la matriz de referencia. |
| `panel_sintetico_resultados.json` | Corrida de referencia con W corregida por empates y 3 × 1.000 réplicas | `code/panel_sintetico.py` (semilla maestra 2026). |

**Alcance.** Las réplicas emulan paramétricamente la matriz de referencia; su
acuerdo mide la estabilidad de las reglas de decisión del protocolo frente a la
composición y el tamaño del panel, y no certifica la validez sustantiva de la
taxonomía. El procedimiento exacto con que se produjo la matriz de referencia
(generador, instrucciones y fecha) no está versionado en este repositorio y se
declara como limitación.
