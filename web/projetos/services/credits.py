
# projetos/services/credits.py
from __future__ import annotations
from dataclasses import dataclass

@dataclass
class EstimateInput:
    images: int                 # declarado no Q3
    products_count: int         # Q3 Produtos selecionados
    ortho_cm: float | None      # Q4
    gsd: float | None           # Q2/Q3

def estimate_credits(inp: EstimateInput) -> int:
    # Mesma lógica que já existe na sua view, só centralizada aqui.
    base = 10
    per_prod = 5 * max(0, inp.products_count)
    res_factor = 0.0
    if inp.ortho_cm:
        res_factor = max(0.0, (3.0 - float(inp.ortho_cm))) * 4.0
    gsd_factor = 0.0
    if inp.gsd:
        gsd_factor = max(0.0, (2.5 - float(inp.gsd))) * 3.0

    unit = max(int(round(base + per_prod + res_factor + gsd_factor)), base)
    return unit * max(0, int(inp.images))
