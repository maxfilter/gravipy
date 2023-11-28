"""Elevation corrections for gravity data."""
import numpy as np
import math

G=6.67*10^(-11) #gravitational constant [N*m^2/kg^2]
r_eq=6378.137*10^3 #equatorial radius [m]
rho_cr=2670 #density of crust [kg/m^3]

def free_air_correction(g_n: np.ndarray, H: np.ndarray) -> np.ndarray:

    dg_free = 2.*H*g_n/r_eq

    return dg_free

def bouguer_plate_correction(H: np.ndarray) -> np.ndarray:

    dg_bp = 2.*math.pi*rho_cr*G*H

    return dg_bp
