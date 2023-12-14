#!/usr/bin/env python3

import os
import math
import numpy as np
import harmonica as hm
import xarray as xr
import rioxarray as rioxr
import verde as vd
import pyproj

'''Generates terrain corrections'''

# should localize the DEM files over Boston region, extract then merge into dem.tif
os.system(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'localize_dems.sh'))

def terrain_correction(elevations: np.ndarray, latitude, longitude, radius=5, water_density=1040., land_density=2670.) -> np.ndarray:
    """Generates vertical gravimeter terrain corrections using a 3d rectangular prism model.
        Radius can be larger for higher elevations, and/or rough terrain.

    Args:
        elevations: array that holds the elevation measurements (in meters)
        latitude: decimal latitude of measurement location
        longitude: decimal longitude of measurement location
        radius: distance in km that terrain corrections are integrated over
    Returns:
        array of vertical corrections in mGal
    """
    if not os.path.exists('dem.tif'):
        raise Exception('./dem.tif missing: cannot generate terrain corrections. Try running ./localize_dems.sh')
    # load the dem into a data_array
    topo = rioxr.open_rasterio('dem.tif').to_dataset('band').to_array()
    n = len(elevations)
    region = get_bounds(latitude, longitude, radius) # select the region based on lat/lon/radius
    topography = topo.sel(
        x=slice(region[0], region[1]),
        y=slice(region[2], region[3]),
    )
    projection = pyproj.Proj(proj="merc", lat_ts=latitude) # use mercator for given lat
    topography_proj = vd.project_grid(topography[0], projection, method="nearest") # project into merc
    # now 3d model topo with rectangular prisms
    density = np.where(topography_proj >= 0, land_density, water_density - land_density) # anything 0 or under is water
    prisms = hm.prism_layer(
        (topography_proj.easting, topography_proj.northing),
        surface=topography_proj,
        reference=0,
        properties={"density": density},
    )
    # Project the coordinates of the observation points
    easting, northing = projection(np.full(n, longitude), np.full(n, latitude))
    coordinates = (easting, northing, elevations)
    # Compute the terrain effect
    terrain_effect = prisms.prism_layer.gravity(coordinates, field="g_z")
    return terrain_effect

def get_bounds(lat, lon, radius):
    '''helper function. Args: lat/lon decimal degrees, radius in km
    Returns: W, E, N, S bounds, in decimal degrees. approximate.'''
    earth_radius = 6371  # Earth's radius in kilometers
    lat_rad = math.radians(lat)
    lon_rad = math.radians(lon)
    rad_lat = radius / earth_radius
    rad_lon = radius / (earth_radius * math.cos(math.pi * lat / 180))
    north = lat + math.degrees(rad_lat)
    south = lat - math.degrees(rad_lat)
    east = lon + math.degrees(rad_lon)
    west = lon - math.degrees(rad_lon)
    return west, east, north, south


if __name__ == '__main__':
    # test terrain corrections for EAPS building location, with various elevations.
    elevations = [2.,22.,2000.]
    latitude=42.36051
    longitude=-71.08927
    radius=5.
    corrections = terrain_correction(elevations, latitude, longitude, radius=radius)
    print('Terrain Corrections')
    for cor, ele in zip(corrections, elevations):
        print(f'{ele:10.1f} (m): {cor:6.4f} (mGal)')
