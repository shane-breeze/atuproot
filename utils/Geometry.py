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
