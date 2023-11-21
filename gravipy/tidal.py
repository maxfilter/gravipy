"""Tidal corrections for gravity data."""
from datetime import datetime
from typing import List
import numpy as np


def tidal_correction(g_measured: np.ndarray, dates: List[datetime]) -> np.ndarray:
    return np.zeros_like(g_measured)
