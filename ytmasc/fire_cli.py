# experiment

import os
import sys

import fire

# abomination
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from ytmasc.tasks import Tasks

fire.Fire(Tasks)
