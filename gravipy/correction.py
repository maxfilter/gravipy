"""Methods for computing gravity corrections and anomalies."""
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
import tidegravity as tide

# constants
G = 6.673e-11  # Newton's gravitational constant [m^3/kg/s^2]
R_EQUATOR = 6378.137e3  # equatorial radius [m]
RHO_CRUST = 2670  # density of crust [kg/m^3]

# unit conversions
# gravitational acceleration [m/s^2] to gravity anomaly [mGal]
accel_to_mGal = lambda a: a * 1e5


def drift_correction(df: pd.DataFrame, base_station_id: str):
    """Computes drift correction for each gravimeter.

    The drift correction is computed by fitting a linear model to the base station
    gravity measurements (with nonlinear tidal correction applied) for each gravimeter.

    Drift corrections are computed relative to the first base station measurement of each
    gravimeter.

    To correct the measured gravity, the drift correction is subtracted from the measured
    gravity.

    Args:
        df: gravimeter data with computed tidal corrections.
        base_station_id: base station site identifier.

    Returns:
        drift correction for each measurement in mGals.
    """
    correction = np.zeros(df.shape[0])

    # apply nonlinear tidal correction (all other corrections are linear)
    g = df["g_measured [mGal]"] - df["tidal correction [mGal]"]

    # convert time to Julian date float
    t = pd.DatetimeIndex(df["time"]).to_julian_date()

    # get indices of base station measurements
    is_base_station = df["site id"].astype("string") == str(base_station_id)

    # fit linear model to base station measurements for each gravimeter
    # since each gravimeter may have a different drift rate
    for gravimeter in df["device"].unique():
        is_current_device = df["device"] == gravimeter

        # fit model to base station measurements
        g_base = g[is_base_station & is_current_device].to_numpy()
        t_base = t[is_base_station & is_current_device].to_numpy()

        X = t_base.reshape(-1, 1)
        y = g_base

        model = LinearRegression().fit(X, y)

        # apply drift correction to all measurements for this gravimeter
        # relative to the first base station measurement
        X_pred = t[is_current_device].to_numpy().reshape(-1, 1)
        device_correction = model.predict(X_pred) - g_base[0]

        correction[is_current_device] = device_correction

    return correction


def compute_corrections(df: pd.DataFrame, base_station_id: str):
    """Computes corrections to measured gravity.

    Args:
        df: dataframe of loaded gravimeter data.
        base_station_id: base station site identifier, used for drift corrections.

    Returns:
        df: original dataframe with appended corrections and anomalies.
    """
    df["g_normal [mGal]"] = accel_to_mGal(df["g_normal [m/s^2]"])

    _, _, df["tidal correction [mGal]"] = tide.solve_longman_tide(
        df["lat"],
        df["lon"],
        df["alt [m]"],
        pd.DatetimeIndex(df["time"]).to_pydatetime(),
    )

    df["drift correction [mGal]"] = drift_correction(df, base_station_id)

    # units check: [m] * [m/s^2] * [1/m] -> [m / s^2]
    df["free air correction [mGal]"] = accel_to_mGal(
        2 * df["orthometric height [m]"] * df["g_normal [m/s^2]"] / R_EQUATOR
    )

    # units check: [kg / m^3] * [m^3 / kg / s^2] * [m] -> [m / s^2]
    df["bouguer plate correction [mGal]"] = accel_to_mGal(
        2 * np.pi * RHO_CRUST * G * df["orthometric height [m]"]
    )

    # compute anomalies
    df["free air anomaly [mGal]"] = (
        df["g_measured [mGal]"]
        + df["tidal correction [mGal]"]
        - df["drift correction [mGal]"]
        + df["free air correction [mGal]"]
        - df["g_normal [mGal]"]
    )

    df["bouguer anomaly [mGal]"] = (
        df["free air anomaly [mGal]"] - df["bouguer plate correction [mGal]"]
    )

    return df
