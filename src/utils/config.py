from pathlib import Path
import os
from dotenv import load_dotenv
ROOT = Path(__file__).resolve().parents[2]
load_dotenv(ROOT / '.env')
DATA = ROOT / 'data'
MODELS = ROOT / 'models'
REPORTS = ROOT / 'reports'
POLICIES = DATA / 'policies'
INDEX = ROOT / 'vector_store'
IBM = DATA / 'attrition/WA_Fn-UseC_-HR-Employee-Attrition.csv'
SEED = 42
EMBEDDING_MODEL = os.getenv('EMBEDDING_MODEL', 'sentence-transformers/all-MiniLM-L6-v2')
