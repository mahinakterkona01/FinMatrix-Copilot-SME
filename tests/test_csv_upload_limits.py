import ast
from io import BytesIO
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
SOURCE = (ROOT / "app.py").read_text(encoding="utf-8-sig")
TREE = ast.parse(SOURCE)
NODE = next(
    node for node in TREE.body
    if isinstance(node, ast.FunctionDef) and node.name == "read_csv_bytes"
)
NAMESPACE = {
    "pd": pd,
    "MAX_CSV_BYTES": 10 * 1024 * 1024,
    "MAX_CSV_ROWS": 100_000,
    "MAX_CSV_COLUMNS": 100,
}
# The function's Streamlit cache decorator is UI infrastructure, not parser logic.
NODE.decorator_list = []
exec(compile(ast.Module(body=[NODE], type_ignores=[]), str(ROOT / "app.py"), "exec"), NAMESPACE)
read_csv_bytes = NAMESPACE["read_csv_bytes"]

def test_valid_csv_parses():
    df = read_csv_bytes(b"inflow,outflow\n100,20\n")
    assert list(df.columns) == ["inflow", "outflow"]
    assert len(df) == 1

@pytest.mark.parametrize("payload", [b"", b"   \n"])
def test_empty_csv_rejected(payload):
    with pytest.raises(ValueError):
        read_csv_bytes(payload)

def test_file_size_limit():
    with pytest.raises(ValueError, match="10 MB"):
        read_csv_bytes(b"x" * (10 * 1024 * 1024 + 1))

def test_row_limit():
    payload = ("inflow,outflow\n" + "1,0\n" * 100_001).encode()
    with pytest.raises(ValueError, match="100,000-row"):
        read_csv_bytes(payload)

def test_column_limit():
    header = ",".join(f"c{i}" for i in range(101))
    payload = (header + "\n" + ",".join("1" for _ in range(101)) + "\n").encode()
    with pytest.raises(ValueError, match="100-column"):
        read_csv_bytes(payload)
