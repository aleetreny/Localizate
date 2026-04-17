from pathlib import Path


BACKEND_ROOT = Path(__file__).resolve().parents[2]
PROJECT_ROOT = BACKEND_ROOT.parent
FRONTEND_ROOT = PROJECT_ROOT / "front"
STORAGE_DIR = PROJECT_ROOT / "storage"
RAW_DATA_DIR = STORAGE_DIR / "raw"
DATA_DIR = STORAGE_DIR / "data"
MODELS_DIR = STORAGE_DIR / "models"
CONFIGS_DIR = BACKEND_ROOT / "configs"
DOCS_DIR = PROJECT_ROOT / "docs"
DOCS_DATA_DIR = DOCS_DIR / "data"
DOCS_PRODUCT_DIR = DOCS_DIR / "product"
DOCS_MODELING_DIR = DOCS_DIR / "modeling"
DOCS_PROJECT_DIR = DOCS_DIR / "project"
DOCS_REFERENCE_DIR = DOCS_DIR / "reference"
