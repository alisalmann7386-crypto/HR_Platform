import json
from datetime import datetime, timezone
from pathlib import Path

def timestamp(): return datetime.now(timezone.utc).isoformat()
def employee_ids(frame):
    values = frame['EmployeeNumber']
    if values.isna().any() or (values % 1 != 0).any() or values.duplicated().any():
        raise ValueError('EmployeeNumber must contain unique non-missing integers.')
    return 'EMP-' + values.astype(int).astype(str)
def save_json(path, value):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(value, indent=2, default=str))
def read_json(path): return json.loads(Path(path).read_text())
