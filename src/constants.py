import os
from typing import Dict, List

# TODO: this is an over-simplification of the degree requirements. For the next version, we need to incorporate
# a more accurate version of this
DEPARTMENT_REQUIREMENT: Dict[str, Dict[str, int]] = {
    "CS": {"foundation": 10, "depth": 27, "breadth": 9, "elective": 0},
    "EE": {"foundation": 0, "depth": 12, "breadth": 9, "elective": 24},
    "CME": {"foundation": 12, "depth": 0, "breadth": 18, "elective": 15},
}
CS_AI_PROGRAM_FILE = os.path.join("data", "cs_ai_requirements.csv")


INDEX_QUARTER: List[str] = ["Autumn", "Winter", "Spring", "Summer"]

MIN_UNITS_PER_QUARTER = 8
MAX_UNITS_PER_QUARTER = 12
MAX_CLASS_REWARD = 5

CONFIG_FOLDER = "configs"
