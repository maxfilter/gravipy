"""Get normal gravity from reference ellipsoid."""
import numpy as np 

def normal_gravity(lat: np.ndarray) -> np.ndarray:
    """ Returns normal (theoretical) gravity at the input latitude, where the gravity is calculated based on the global reference ellipsoid given by Geodetic Reference System 1980 (c.f. Equation (5.73) in Geodynamics (2e) by Turcotte, Schubert). 
    
    Args: 
        lat: Array of latitudes 
    Output: 
        Returns array of normal gravity corresponding to latitudes
        
        """
    g_normal = 9.7803267715*(1 + 0.0052790414* np.power(np.sin(lat), 2) + 0.0000232718 * np.power(np.sin(lat), 4) + 0.0000001262* np.power(np.sin(lat), 6) +0.0000000007 * np.power(np.sin(lat), 8))
    
    return g_normal
