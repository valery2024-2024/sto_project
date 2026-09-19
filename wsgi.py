import importlib.util
from pathlib import Path


app_path = Path(__file__).resolve().parent / "app.py"
spec = importlib.util.spec_from_file_location("sto_root_app", app_path)
module = importlib.util.module_from_spec(spec)

if spec.loader is None:
    raise RuntimeError("Unable to load root app.py")

spec.loader.exec_module(module)
app = module.app
