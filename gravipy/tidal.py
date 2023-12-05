"""Tidal corrections for gravity data."""
from datetime import datetime
from typing import List
import numpy as np
import pandas as pd
import tidegravity as tide

# def tidal_correction(g_measured: np.ndarray, dates: List[datetime]) -> np.ndarray:
#     return np.zeros_like(g_measured)

def tidal_correction(df: pd.DataFrame) -> pd.DataFrame:
    # df has columns [lat], [lon], [alt], and time columns [year], [month], 
    # [day], [hour], [minute]

    tidal_corrections = np.zeros(len(df))
    # Iterate through each row of the dataframe and calculate the tidal correction
    for index, row in df.iterrows():
        year = row["year"]
        month = row["month"]
        day = row["day"]
        hour = row["hour"]
        minute = row["minute"]
        time = datetime(year, month, day, hour, minute)

        lat = row["lat"]
        lon = row["lon"] # west should be entered as negative value
        alt = row["orthometric height"]
        
        mg_correction = tide.solve_longman_tide_scalar(lat, lon, alt, time)
        tidal_corrections[index] = mg_correction[-1]

    return tidal_corrections