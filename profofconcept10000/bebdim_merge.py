#!/usr/bin/env python3
"""
BEBDiM (strict) with optional auto-padding, integer-only adjacency matrices (>= 0).

Merge rule (strict):
  - A in top-left, B in bottom-right
  - zeros elsewhere
  - single bridge at D[0, a] = 1  (a = size of A)

Inputs (Base64 JSON):
  - combined_b64_X: {"nodes": [... or { "0": "...", ...}], "matrix": [[...], ...]}
    (You may also load separate matrix_b64/nodes_b64 if you adapt callers; this file focuses on combined_b64.)

High-level API:
  merge_two_networks_from_b64_strict(..., allow_autopad=True|False) -> dict
  Returned dict includes:
    - combined_b64: Base64(JSON {"nodes":{...},"matrix":[[...] ...]})  <-- use this

Run this file directly to see a demo with your two provided Base64 blobs.
"""

from __future__ import annotations
import base64
import json
from typing import Dict, List, Tuple, Optional, Any
import numpy as np


# ---------- Base64 helpers ----------
def _b64_decode_json(b64_str: str) -> Any:
    data = base64.b64decode(b64_str.encode("utf-8"))
    return json.loads(data.decode("utf-8"))

def _b64_encode_json(obj: Any) -> str:
    raw = json.dumps(obj, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return base64.b64encode(raw).decode("utf-8")


# ---------- Nodes parsing ----------
def _as_index_name_map(nodes_any: Any) -> Dict[int, str]:
    """
    Accept nodes as:
      - list[str]  (index by position)
      - dict[int|str, str]  (index -> name)
    Converts keys to integers automatically.
    Returns a dict[int, str].
    """
    if isinstance(nodes_any, list):
        return {i: str(name) for i, name in enumerate(nodes_any)}
    if isinstance(nodes_any, dict):
        out: Dict[int, str] = {}
        for k, v in nodes_any.items():
            try:
                idx = int(k)
            except Exception as e:
                raise ValueError(f"Node map keys must be int-like; bad key={k!r}") from e
            out[idx] = str(v)
        return out
    raise ValueError("Nodes must be a list[str] or dict[int,str].")


# ---------- Matrix validation / padding ----------
def _validate_or_pad_matrix(
    m: Any,
    n_expected: int,
    allow_autopad: bool,
) -> Tuple[np.ndarray, Dict[str, int]]:
    """
    Build an int64 adjacency matrix of shape (n_expected, n_expected).
    - Values must be integer-like >= 0.
    - If allow_autopad=True, pad missing rows/cols with zeros up to n_expected.
    - If any row is longer than n_expected, raise (never truncate).
    - If there are more than n_expected rows, raise (never truncate).

    Returns:
        (matrix, {"added_rows": int, "added_cols_max": int})
    """
    if not isinstance(m, list):
        raise ValueError("Matrix must be a list of rows.")
    rows_raw: List[List[Any]] = []
    for i, row in enumerate(m):
        if not isinstance(row, list):
            raise ValueError(f"Row {i} is not a list.")
        rows_raw.append(row)

    # Convert values to int >= 0; track max original row length
    max_len = 0
    norm_rows: List[List[int]] = []
    for i, row in enumerate(rows_raw):
        new_row: List[int] = []
        for j, v in enumerate(row):
            if isinstance(v, int) or (isinstance(v, float) and float(v).is_integer()):
                iv = int(v)
            else:
                try:
                    iv = int(v)
                except Exception as e:
                    raise ValueError(f"Matrix value at ({i},{j}) is not integer-like: {v!r}") from e
            if iv < 0:
                raise ValueError(f"Matrix contains negative value at ({i},{j}).")
            new_row.append(iv)
        max_len = max(max_len, len(new_row))
        norm_rows.append(new_row)

    # Too wide?
    if max_len > n_expected:
        raise ValueError(f"Matrix has row(s) width {max_len} > nodes {n_expected} (no truncation allowed).")

    # Too many rows?
    if len(norm_rows) > n_expected:
        raise ValueError(f"Matrix has {len(norm_rows)} rows > nodes {n_expected} (no truncation allowed).")

    # If autopad is off, enforce exact n x n
    if not allow_autopad:
        if len(norm_rows) != n_expected or max_len != n_expected:
            raise ValueError(
                f"Matrix must be square {n_expected}x{n_expected}, got {len(norm_rows)}x{max_len}. "
                f"Enable auto-padding or fix the source."
            )

    # Pad rows to length n_expected (if short)
    padded_rows: List[List[int]] = []
    added_cols_max = 0
    for r in norm_rows:
        add_cols = n_expected - len(r)
        if add_cols < 0:
            # caught earlier; defensive
            raise ValueError("Unexpected negative padding.")
        if add_cols > 0 and allow_autopad:
            r = r + [0] * add_cols
            added_cols_max = max(added_cols_max, add_cols)
        padded_rows.append(r)

    # Pad missing rows up to n_expected
    added_rows = 0
    if len(padded_rows) < n_expected and allow_autopad:
        zero_row = [0] * n_expected
        missing = n_expected - len(padded_rows)
        padded_rows.extend([zero_row[:] for _ in range(missing)])
        added_rows = missing

    # If still not exact (auto-pad off), raise
    if len(padded_rows) != n_expected or any(len(r) != n_expected for r in padded_rows):
        raise ValueError(
            f"Matrix dimensions invalid after checks: {len(padded_rows)}x"
            f"{max(len(r) for r in padded_rows)}; expected {n_expected}."
        )

    return np.array(padded_rows, dtype=np.int64), {"added_rows": added_rows, "added_cols_max": added_cols_max}


# ---------- Loaders ----------
def load_network_from_b64(
    *,
    matrix_b64: Optional[str] = None,
    nodes_b64: Optional[str] = None,
    combined_b64: Optional[str] = None,
    allow_autopad: bool = True,
) -> Tuple[np.ndarray, Dict[int, str], Dict[str, int]]:
    """
    Load a network (matrix + nodes) from Base64 and return:
        (A, nodes_map, pad_info)
    Where pad_info = {"added_rows": int, "added_cols_max": int}
    """
    if combined_b64:
        obj = _b64_decode_json(combined_b64)
        if "matrix" not in obj or "nodes" not in obj:
            raise ValueError("combined_b64 JSON must contain 'matrix' and 'nodes'.")
        nodes_map = _as_index_name_map(obj["nodes"])
        n = len(nodes_map)
        A, pad_info = _validate_or_pad_matrix(obj["matrix"], n, allow_autopad)
        return A, nodes_map, pad_info

    if not (matrix_b64 and nodes_b64):
        raise ValueError("Provide either (matrix_b64 AND nodes_b64) OR combined_b64.")

    mat = _b64_decode_json(matrix_b64)
    nod = _b64_decode_json(nodes_b64)

    nodes_map = _as_index_name_map(nod)
    n = len(nodes_map)
    A, pad_info = _validate_or_pad_matrix(mat, n, allow_autopad)
    return A, nodes_map, pad_info


# ---------- BEBDiM (strict bridge at D[0, a] = 1) ----------
def strict_merge_A_top_left_B_bottom_right(A: np.ndarray, B: np.ndarray) -> np.ndarray:
    """
    Build D of shape (a+b, a+b):
      - D[:a, :a] = A
      - D[a:, a:] = B
      - zeros elsewhere
      - D[0, a] = 1  (single bridge from first node of A to first node of B)
    """
    a, b = A.shape[0], B.shape[0]
    D = np.zeros((a + b, a + b), dtype=np.int64)
    D[:a, :a] = A
    D[a:, a:] = B
    D[0, a] = 1
    return D

def merge_node_maps(nodesA: Dict[int, str], nodesB: Dict[int, str]) -> Dict[int, str]:
    out = {i: name for i, name in nodesA.items()}
    offset = len(nodesA)
    for j, name in nodesB.items():
        out[offset + j] = name
    return out


# ---------- High-level API ----------
def merge_two_networks_from_b64_strict(
    *,
    matrix_b64_A: Optional[str] = None,
    nodes_b64_A: Optional[str] = None,
    combined_b64_A: Optional[str] = None,
    matrix_b64_B: Optional[str] = None,
    nodes_b64_B: Optional[str] = None,
    combined_b64_B: Optional[str] = None,
    allow_autopad: bool = True,
) -> Dict[str, Any]:
    """
    Strict BEBDiM merge with optional auto-padding.
    Returns:
      {
        "nodes_map": {idx: name, ...},
        "nodes_list": [...],
        "matrix": [[...], ...],
        "combined_b64": "<Base64(JSON {'nodes':{...}, 'matrix':[[...]]})>",
        "padding": {"A": {...}, "B": {...}},
        "sizes": {"A": a, "B": b, "D": a+b}
      }
    """
    A, nodesA, padA = load_network_from_b64(
        matrix_b64=matrix_b64_A,
        nodes_b64=nodes_b64_A,
        combined_b64=combined_b64_A,
        allow_autopad=allow_autopad,
    )
    B, nodesB, padB = load_network_from_b64(
        matrix_b64=matrix_b64_B,
        nodes_b64=nodes_b64_B,
        combined_b64=combined_b64_B,
        allow_autopad=allow_autopad,
    )

    D = strict_merge_A_top_left_B_bottom_right(A, B)
    merged_nodes_map = merge_node_maps(nodesA, nodesB)
    nodes_list = [merged_nodes_map[i] for i in range(len(merged_nodes_map))]

    # Build the expected combined JSON object: {"nodes": {"0": "name0", ...}, "matrix": [[...], ...]}
    matrix_py: List[List[int]] = D.tolist()
    nodes_json_obj = {str(i): merged_nodes_map[i] for i in range(len(merged_nodes_map))}
    combined_obj = {"nodes": nodes_json_obj, "matrix": matrix_py}
    combined_b64 = _b64_encode_json(combined_obj)

    # Kept raw artifacts & diagnostics for convenience
    return {
        "nodes_map": merged_nodes_map,
        "nodes_list": nodes_list,
        "matrix": matrix_py,
        "combined_b64": combined_b64,  # <-- use this
        "padding": {"A": padA, "B": padB},
        "sizes": {"A": int(A.shape[0]), "B": int(B.shape[0]), "D": int(D.shape[0])},
    }


# ---------- Pretty output ----------
def print_merge_result(result: Dict[str, Any]) -> None:
    print("=== Merged Nodes (index -> name) ===")
    for i, name in enumerate(result["nodes_list"]):
        print(f"{i}: {name}")

    print("\n=== Merged Matrix D ===")
    for row in result["matrix"]:
        print(row)

    print("\n=== Merged Graph (Base64 JSON with 'nodes' + 'matrix') ===")
    print(result["combined_b64"])

    if "padding" in result and "sizes" in result:
        print("\n=== Diagnostics ===")
        padA = result["padding"]["A"]
        padB = result["padding"]["B"]
        sizes = result["sizes"]
        print(f"A size: {sizes['A']}  | padding A -> rows+{padA['added_rows']} cols(max)+{padA['added_cols_max']}")
        print(f"B size: {sizes['B']}  | padding B -> rows+{padB['added_rows']} cols(max)+{padB['added_cols_max']}")
        print(f"Final D size: {sizes['D']}")


# ---------- Demo ----------
if __name__ == "__main__":
    # Your provided Base64 networks (combined form with "nodes" + "matrix"):
    combined_b64_A = "eyJub2RlcyI6IHsiMCI6ICJhbW8iLCAiMSI6ICJNaWd1ZWwwMzQyIiwgIjIiOiAiRGF2aWQ0NjgwIiwgIjMiOiAiQmFkYTY2NTAiLCAiNCI6ICJGcmFuNTIyOCIsICI1IjogIkhlbnJpOTc3MyIsICI2IjogIkphaW1lMDEzNyIsICI3IjogIkphaW1lMDg3NCIsICI4IjogIkpvcmdlODEyOCIsICI5IjogIlJ1YmVuODMyOSIsICIxMCI6ICJKdWFuMDc1MyIsICIxMSI6ICJNYW5vbG8wNDk2IiwgIjEyIjogIk1pZ3VlbDAyODgiLCAiMTMiOiAiTW9pc2VzMzQ3NyIsICIxNCI6ICJGaXRvMTM1MiIsICIxNSI6ICJQaWxhcjg2NTYiLCAiMTYiOiAiQW5kcmVhMTYzMyIsICIxNyI6ICJFbGVuYTc3MTMifSwgIm1hdHJpeCI6IFtbMCwgMCwgMCwgMCwgMCwgMCwgMCwgMCwgMCwgMCwgMCwgMCwgMCwgMCwgMCwgMCwgMCwgMF0sIFswLCAwLCAwLCAwLCAwLCAwLCAwLCAwLCAwLCAwLCAwLCAwLCAwLCAwLCAwLCAwLCAwLCAwXSwgWzAsIDAsIDAsIDAsIDAsIDAsIDAsIDAsIDAsIDAsIDAsIDAsIDAsIDAsIDAsIDAsIDAsIDBdLCBbMCwgMCwgMCwgMCwgMCwgMCwgMCwgMCwgMCwgMCwgMCwgMCwgMCwgMCwgMCwgMCwgMCwgMF0sIFswLCAwLCAwLCAwLCAwLCAwLCAwLCAwLCAwLCAwLCAwLCAwLCAwLCAwLCAwLCAwLCAwLCAwXSwgWzAsIDAsIDAsIDAsIDAsIDAsIDAsIDAsIDAsIDAsIDAsIDAsIDAsIDAsIDAsIDAsIDAsIDBdLCBbMCwgMCwgMCwgMCwgMCwgMCwgMCwgMCwgMCwgMCwgMCwgMCwgMCwgMCwgMCwgMCwgMCwgMF0sIFswLCAwLCAwLCAwLCAwLCAwLCAwLCAwLCAwLCAwLCAwLCAwLCAwLCAwLCAwLCAwLCAwLCAwXSwgWzAsIDAsIDAsIDAsIDAsIDAsIDAsIDAsIDAsIDAsIDAsIDAsIDAsIDAsIDAsIDAsIDAsIDBdLCBbMCwgMCwgMCwgMCwgMCwgMCwgMCwgMCwgMCwgMCwgMCwgMCwgMCwgMCwgMCwgMCwgMCwgMF0sIFswLCAwLCAwLCAwLCAwLCAwLCAwLCAwLCAwLCAwLCAwLCAwLCAwLCAwLCAwLCAwLCAwLCAwXSwgWzAsIDAsIDAsIDAsIDAsIDAsIDAsIDAsIDAsIDAsIDAsIDAsIDAsIDAsIDAsIDAsIDAsIDBdLCBbMCwgMCwgMCwgMCwgMCwgMCwgMCwgMCwgMCwgMCwgMCwgMCwgMCwgMCwgMCwgMCwgMCwgMF1dfQ=="
    combined_b64_B = "eyJub2RlcyI6IHsiMCI6ICJCZW5qYW1pbjkzOTAiLCAiMSI6ICJEYXZpZDY3MDMiLCAiMiI6ICJBbGV4NDk1OCIsICIzIjogIkFsdmFybzk0NjIiLCAiNCI6ICJNYW51Mzc3NiIsICI1IjogIk1pZ3VlbDEwNzUiLCAiNiI6ICJMdWlzNzA4MiIsICI3IjogIktpa28zNDk0IiwgIjgiOiAiSm9zZTAzMDEiLCAiOSI6ICJNYW51ZWwzNTMzIiwgIjEwIjogIlBlcGUxNjQwIiwgIjExIjogIlRpbTkyNzMiLCAiMTIiOiAiUGluYXI0MjczIiwgIjEzIjogIkFsZXNzYW5kcm83MzQ5IiwgIjE0IjogIkRpb2dvMjk5MCIsICIxNSI6ICJDaGVmNTA5NyIsICIxNiI6ICJQZWRybzUxMDAiLCAiMTciOiAiU2FudGlhZ281Njk4IiwgIjE4IjogIlJhdWwyNjI2IiwgIjE5IjogIlZpY3Rvcjg0MDUiLCAiMjAiOiAiUGFibG82ODE0IiwgIjIxIjogIlJpY2FyZG8yNjE2In0sICJtYXRyaXgiOiBbWzAsIDAsIDAsIDAsIDAsIDAsIDAsIDAsIDAsIDAsIDAsIDAsIDAsIDAsIDAsIDAsIDAsIDAsIDAsIDAsIDAsIDBdLCBbMCwgMCwgMCwgMCwgMCwgMCwgMCwgMCwgMCwgMCwgMCwgMCwgMCwgMCwgMCwgMCwgMCwgMCwgMCwgMCwgMCwgMF0sIFswLCAwLCAwLCAwLCAwLCAwLCAwLCAwLCAwLCAwLCAwLCAwLCAwLCAwLCAwLCAwLCAwLCAwLCAwLCAwLCAwLCAwXSwgWzAsIDAsIDAsIDAsIDAsIDAsIDAsIDAsIDAsIDAsIDAsIDAsIDAsIDAsIDAsIDAsIDAsIDAsIDAsIDAsIDAsIDBdLCBbMCwgMCwgMCwgMCwgMCwgMCwgMCwgMCwgMCwgMCwgMCwgMCwgMCwgMCwgMCwgMCwgMCwgMCwgMCwgMCwgMCwgMF0sIFswLCAwLCAwLCAwLCAwLCAwLCAwLCAwLCAwLCAwLCAwLCAwLCAwLCAwLCAwLCAwLCAwLCAwLCAwLCAwLCAwLCAwXSwgWzAsIDAsIDAsIDAsIDAsIDAsIDAsIDAsIDAsIDAsIDAsIDAsIDAsIDAsIDAsIDAsIDAsIDAsIDAsIDAsIDAsIDBdLCBbMCwgMCwgMCwgMCwgMCwgMCwgMCwgMCwgMCwgMCwgMCwgMCwgMCwgMCwgMCwgMCwgMCwgMCwgMCwgMCwgMCwgMF0sIFswLCAwLCAwLCAwLCAwLCAwLCAwLCAwLCAwLCAwLCAwLCAwLCAwLCAwLCAwLCAwLCAwLCAwLCAwLCAwLCAwLCAwXSwgWzAsIDAsIDAsIDAsIDAsIDAsIDAsIDAsIDAsIDAsIDAsIDAsIDAsIDAsIDAsIDAsIDAsIDAsIDAsIDAsIDAsIDBdLCBbMCwgMCwgMCwgMCwgMCwgMCwgMCwgMCwgMCwgMCwgMCwgMCwgMCwgMCwgMCwgMCwgMCwgMCwgMCwgMCwgMCwgMF0sIFswLCAwLCAwLCAwLCAwLCAwLCAwLCAwLCAwLCAwLCAwLCAwLCAwLCAwLCAwLCAwLCAwLCAwLCAwLCAwLCAwLCAwXSwgWzAsIDAsIDAsIDAsIDAsIDAsIDAsIDAsIDAsIDAsIDAsIDAsIDAsIDAsIDAsIDAsIDAsIDAsIDAsIDAsIDAsIDBdLCBbMCwgMCwgMCwgMCwgMCwgMCwgMCwgMCwgMCwgMCwgMCwgMCwgMCwgMCwgMCwgMCwgMCwgMCwgMCwgMCwgMCwgMF0sIFswLCAwLCAwLCAwLCAwLCAwLCAwLCAwLCAwLCAwLCAwLCAwLCAwLCAwLCAwLCAwLCAwLCAwLCAwLCAwLCAwLCAwXSwgWzAsIDAsIDAsIDAsIDAsIDAsIDAsIDAsIDAsIDAsIDAsIDAsIDAsIDAsIDAsIDAsIDAsIDAsIDAsIDAsIDAsIDBdXX0="

    # Toggle auto-padding to square(n x n). True pads; False enforces exact square.
    allow_autopad = True

    result = merge_two_networks_from_b64_strict(
        combined_b64_A=combined_b64_A,
        combined_b64_B=combined_b64_B,
        allow_autopad=allow_autopad,
    )
    print_merge_result(result)

    # To see the strict validator reject the inputs, set allow_autopad=False above.
