# pyre-ignore-all-errors
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import BASE_DIR
from app.services.step2_service import INPUT_DIR

print("BASE_DIR:", BASE_DIR)
print("BASE_DIR.parent:", BASE_DIR.parent)
print("BASE_DIR.parent.parent:", BASE_DIR.parent.parent)
print("INPUT_DIR evaluated to:", INPUT_DIR)
print("Exists?:", os.path.exists(INPUT_DIR))

if os.path.exists(INPUT_DIR):
    print("Files:", os.listdir(INPUT_DIR))
