import numpy as np
from numpy import pi
from numba import njit

@njit(cache=True)
def BoundPhi(phi):
    if phi >= pi:
        phi -= 2*pi
    elif phi < -pi:
        phi += 2*pi
    return phi

@njit(cache=True)
def DeltaR2(deta, dphi):
    return deta**2 + BoundPhi(dphi)**2

@njit(cache=True)
def RadToCart(r, phi):
    return r*np.cos(phi), r*np.sin(phi)

@njit(cache=True)
def CartToRad(x, y):
    return np.sqrt(x**2+y**2), BoundPhi(np.arctan2(y, x))

@njit(cache=True)
def LorTHPMToXYZE(t, h, p, m):
    x = t*np.cos(p)
    y = t*np.sin(p)
    z = t*np.sinh(h)
    e = np.sqrt(m**2 + t**2 + z**2)
    return x, y, z, e

@njit(cache=True)
def LorXYZEToTHPM(x, y, z, e):
    t = np.sqrt(x**2+y**2)
    h = np.arctanh(z/np.sqrt(t**2+z**2))
    p = BoundPhi(np.arctan2(y, x))
    m2 = e**2 - t**2 - z**2
    m = np.sign(m2) * np.sqrt(abs(m2))
    return t, h, p, m
