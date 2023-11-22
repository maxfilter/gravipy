"""Main correction function that takes in path to a csv file and applies all necessary corrections."""

from datetime import datetime
from typing import List

import pandas as pd
import numpy as np

from gravipy.drift import instrument_drift_correction
from gravipy.elevation import (
    free_air_correction,
    bouguer_plate_correction,
    latitude_correction,
)
from gravipy.tidal import tidal_correction


def parse_dates(df: pd.DataFrame) -> List[datetime]:
    """Parses dates from dataframe into datetime format.

    Args:
        df: Dataframe with year, month, day, hour, minute columns.

    Returns:
        List of python datetimes.
    """
    dates = []
    for _, row in df.iterrows():
        year = int(row["year"])
        month = int(row["month"])
        day = int(row["day"])
        hour = int(row["hour"])
        minute = int(row["minute"])
        dates.append(datetime(year, month, day, hour, minute))

    return dates


def raw_to_mgal(raw: np.ndarray):
    """Converts raw gravimeter data to milligals."""
    # todo: implement
    return raw


def correct(data_path: str):
    """Corrects measured gravity for elevation, tidal, and instrument drift effects.

    Args:
        data_path: Path to csv data file.

    Returns:
        Dataframe with corrected gravity values.
    """
    # load data
    df = pd.read_csv(data_path)
    dates = parse_dates(df)
    lat = np.full(len(dates), 42.3603)  # todo: read from df
    gravimeter_raw = df["raw"].to_numpy()

    # convert gravimeter raw data to mgal
    g_measured = raw_to_mgal(gravimeter_raw)

    # calculate corrections
    df["latitude_correction"] = latitude_correction(g_measured, lat)
    df["freeair_correction"] = free_air_correction(g_measured)
    df["bouguer_correction"] = bouguer_plate_correction(g_measured)
    df["tides_correction"] = tidal_correction(g_measured, dates)
    df["drift_correction"] = instrument_drift_correction(g_measured, dates)

    # todo: compute final anomaly

    return df
