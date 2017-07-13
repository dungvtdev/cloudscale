import sys
import os

base_path = os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.dirname(__file__))))
base_path = os.path.abspath(base_path)

sys.path.append(base_path)