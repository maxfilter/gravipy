"""Methods for loading and preprocessing gravimeter measurements."""
import os

import geopandas as gpd
import numpy as np
import pandas as pd
from shapely import box

WGS84_EPSG = 4326
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
GMC_ZIP_URL = "https://www.conservation.ca.gov/cgs/Documents/Publications/Geologic-Data-Maps/GDM_002_GMC_750k_v2_GIS.zip"
GMC_GEO_POLY_SHAPEFILE_PATH = "shapefiles/GMC_geo_poly.shp"
GMC_GEOLOGY_URL = f"/vsizip/vsicurl/{GMC_ZIP_URL}/{GMC_GEO_POLY_SHAPEFILE_PATH}"
CATALINA_WGS84_BBOX_COORDS = (-118.635060, 33.268233, -118.261344, 33.504121)


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


def _check_columns(df: pd.DataFrame):
    """Verify that all required columns are present in dataframe."""
    missing_cols = []
    for col in REQUIRED_COLS:
        if col not in df.columns:
            missing_cols.append(col)

    if len(missing_cols):
        raise ValueError(f"Missing required columns: {missing_cols} in dataframe.")

def load_geology():
    bbox = gpd.GeoDataFrame({'geometry': [box(*CATALINA_WGS84_BBOX_COORDS)]}, crs=WGS84_EPSG)
    return gpd.read_file(GMC_GEOLOGY_URL, bbox=bbox).to_crs(WGS84_EPSG).clip(bbox).set_index("PTYPE").drop("water")

def load_geology_map_key(data_dir: str = "data", data_file: str = "GMC_map_key.xls"):
    return pd.read_excel(os.path.join(data_dir, data_file), index_col="PTYPE")


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
    # load raw data and verify that all required columns are present
    df = pd.read_csv(os.path.join(data_dir, data_file))
    _check_columns(df)

    df["time"] = pd.to_datetime(df[TIME_COLS])
    df["g_measured [mGal]"] = counter_to_mGal(df["counter"], df["device"], data_dir)
    df["g_normal [m/s^2]"] = normal_gravity(df["lat"])

    # build GeoDataFrame
    geometry = gpd.points_from_xy(df["lon"], df["lat"])
    gdf = gpd.GeoDataFrame(df, geometry=geometry, crs=WGS84_EPSG)

    # include geology unit type for each feature
    geology = load_geology()
    gdf["geology"] = [geology.index[geology.contains(point)][0] for point in gdf.geometry]
    
    return gdf