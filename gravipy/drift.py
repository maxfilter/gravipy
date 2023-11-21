"""Instrument drift corrections"""

from datetime import datetime
from typing import List

import numpy as np


def instrument_drift_correction(
    g_measured: np.ndarray, dates: List[datetime]
) -> np.ndarray:
    """TODO

    Args:
        g_measured: TODO
        dates: TODO
    """
    return np.zeros_like(g_measured)
