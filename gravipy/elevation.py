"""Elevation corrections for gravity data."""
import numpy as np


def latitude_correction(g_measured: np.ndarray, lat: np.ndarray) -> np.ndarray:
    return np.zeros_like(g_measured)


def free_air_correction(g_measured: np.ndarray) -> np.ndarray:
    return np.zeros_like(g_measured)


def bouguer_plate_correction(g_measured: np.ndarray) -> np.ndarray:
    return np.zeros_like(g_measured)
