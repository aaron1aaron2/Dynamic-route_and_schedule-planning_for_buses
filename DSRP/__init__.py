#!/usr/bin/env python3
# encoding: utf-8
"""
Author: yen-nan ho
Contact: aaron1aaron2@gmail.com
GitHub: https://github.com/aaron1aaron2
Create Date:  20210907
"""

import os
import sys
import pathlib 

if sys.version_info < (3, 7):
    raise RuntimeError('DSRP supports Python 3.7 or higher.')

PROJECT_PATH = str(pathlib.PurePath(__file__).parent.parent)
DATA_DIR = (
    os.path.join(PROJECT_PATH, 'data')
)
if not os.path.exists(DATA_DIR):
    raise RuntimeError(f'DSRP not find data folder at : {DATA_DIR}')

from . import path_planing
from . import visualization
from . import utils