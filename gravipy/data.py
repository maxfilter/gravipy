"""Methods for loading and preprocessing gravimeter measurements."""
import os

import numpy as np
import pandas as pd

TIME_COLS = ["year", "month", "day", "hour", "minute"]
REQUIRED_COLS = TIME_COLS + [
    "lat",
    "lon",
    "alt [m]",
    "device",
    "counter",
    "site id",
    "orthometric height [m]",
]


def counter_to_mGal(raw: np.ndarray, device: np.ndarray, dial_conversion_dir: str):
    """Converts raw gravimeter data to milliGals.

    Args:
        raw: counter reading from gravimeter for each point.
        device: device used to measure gravity for each point ('mit' or 'caltech').
        dial_conversion_dir: path to directory containing dial conversion text files.

    Returns:
        Measured gravity anomaly in mGals.
    """
    result = np.zeros_like(raw, dtype=float)

    for gravimeter in ("mit", "caltech"):
        counter, mGal = np.loadtxt(
            os.path.join(dial_conversion_dir, f"{gravimeter}_dial.txt")
        ).T
        result[device == gravimeter] = np.interp(
            raw[device == gravimeter], counter, mGal
        )

    return result


def normal_gravity(lat: np.ndarray) -> np.ndarray:
    """Computes normal (theoretical) gravity corrected for latitude.

    Uses the global reference ellipsoid given by Geodetic Reference System 1980
    (c.f. Equation (5.73) in Geodynamics (2e) by Turcotte, Schubert).

    Args:
        lat: latitude in decimal degrees

    Returns:
        normal gravity in m/s^2.
    """
    # convert decimal degrees to radians
    phi = lat * np.pi / 180

    return 9.7803267715 * (
        1
        + 0.0052790414 * np.sin(phi) ** 2
        + 0.0000232718 * np.sin(phi) ** 4
        + 0.0000001262 * np.sin(phi) ** 6
        + 0.0000000007 * np.sin(phi) ** 8
    )


def get_measurements_by_id(df: pd.DataFrame, site_id: str):
    """Returns dataframe of measurements for id.

    Args:
        df: dataframe of loaded gravimeter data.
        id: site identifier.

    Returns:
        df: dataframe of base station measurements.
    """
    is_site = df["site id"].astype("string") == str(site_id)
    return df[is_site]


def _check_columns(df: pd.DataFrame):
    """Verify that all required columns are present in dataframe."""
    missing_cols = []
    for col in REQUIRED_COLS:
        if col not in df.columns:
            missing_cols.append(col)

    if len(missing_cols):
        raise ValueError(f"Missing required columns: {missing_cols} in dataframe.")


def load_data(data_dir: str = "data", data_file: str = "gravimeter.csv"):
    """Loads data from csv file of gravimeter measurements.

    gravimeter.csv must contain rows:
    - 'year'/'month'/'day'/'hour'/'minute': date and time of measurement.
    - 'lat': latitude in decimal degrees.
    - 'lon': longitude in decimal degrees.
    - 'alt [m]': altitude in meters.
    - 'device': gravimeter used to measure gravity ('mit' or 'caltech').
    - 'counter': counter reading from gravimeter.
    - 'site id': measurement site identifier. Each site should have a unique identifier.
    - 'orthometric height [m]': height above geoid in meters.

    Args:
        data_dir: path to directory containing data_file.
        data_file: name of csv file containing gravimeter measurements.

    Returns:
        df: dataframe of loaded gravimeter data, with additional columns:
            - 'time': datetime object of measurement.
            - 'g_measured [mGal]': measured gravity in mGals.
            - 'g_normal [m/s^2]': normal gravity in m/s^2.
    """
    df = pd.read_csv(os.path.join(data_dir, data_file))
    _check_columns(df)
    df["time"] = pd.to_datetime(df[TIME_COLS])
    df["g_measured [mGal]"] = counter_to_mGal(df["counter"], df["device"], data_dir)
    df["g_normal [m/s^2]"] = normal_gravity(df["lat"])
    return df
