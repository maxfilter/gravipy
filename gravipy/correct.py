"""Main correction function that takes in path to a csv file and applies all necessary corrections."""

from datetime import datetime
from typing import List

import pandas as pd
import numpy as np

from gravipy.drift import instrument_drift_correction
from gravipy.elevation import (
    free_air_correction,
    bouguer_plate_correction,
)
from gravipy.normal import normal_gravity
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
    """Converts raw gravimeter data to microgals.
    
    Args:
        raw: Dial raw data red from the gravimeter.
    
    Returns:
        Converted raw dial into mgal gravity data.
    """
    # Define interval factor and mgal conv value, values for 3800
    int_factor = 1.05658 
    mgal_val = 4008.94

    # Get the last 2 digits of the number and multiply it by the interval factor
    int_val = abs(raw) % 100
    int_conv = int_val * int_factor

    # Add tens_conv to mgal value
    g_mgal = int_conv + mgal_val
    
    return g_mgal


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
    gravimeter_raw = df["raw"].to_numpy()

    # convert gravimeter raw data to mgal
    g_measured = raw_to_mgal(gravimeter_raw)

    H = df['orthometric height'].to_numpy()
    g_normal = normal_gravity(df['lat'].to_numpy())

    # calculate corrections
    df["freeair_correction"] = free_air_correction(g_normal, H)
    df["bouguer_correction"] = bouguer_plate_correction(H)
    df["tides_correction"] = tidal_correction(df)
    # df["drift_correction"] = instrument_drift_correction(g_measured, dates)

    # todo: compute final anomaly
    df["free air anomaly"] = g_measured + df["freeair_correction"] + df["tides_correction"] - g_normal
    df["bouguer anomaly"] = df["free air anomaly"] - df["bouguer_correction"]

    return df
