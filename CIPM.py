from math import exp
from decimal import *
from numpy import longdouble

def calculateAirDensity(tObs, tc, pObs, pc, rhObs, rhc):
    #Calculates the air density using the CIPM 2007 air density equation
    #Picard et al.: https://iopscience.iop.org/article/10.1088/0026-1394/45/2/004

    getcontext().prec = 28

    temp = Decimal(tObs) - Decimal(tc)
    pressure = Decimal(pObs) - Decimal(pc)
    humidity = Decimal(rhObs) - Decimal(rhc)

    tKelvin = temp + Decimal('273.15')
    humidity = humidity / Decimal('100')
    pressurePa = pressure * (Decimal('101325') / Decimal('760'))

    a = Decimal('0.000012378847')
    b = Decimal('-0.019121316')
    c = Decimal('33.93711047')
    d = Decimal('-6343.1645')

    alpha = Decimal('1.00062')
    beta = Decimal('0.0000000314')
    gamma = Decimal('0.00000056')

    r = Decimal('8.314472')
    ma = Decimal('0.02896546')
    mv = Decimal('0.01801528')

    aZero = Decimal('0.00000158123')
    aOne = Decimal('-0.000000029331')
    aTwo = Decimal('0.00000000011043')
    bZero = Decimal('0.000005707')
    bOne = Decimal('-0.00000002051')
    cZero = Decimal('0.00019898')
    cOne = Decimal('-0.000002376')
    dZ = Decimal('0.0000000000183')
    e = Decimal('-0.00000000765')

    vaporPressure = (a * tKelvin**2 + b * tKelvin + c + d / tKelvin).exp()
    f = alpha + beta * pressurePa + gamma * temp**2
    xv = humidity * f * (vaporPressure / pressurePa)

    z = 1 - (pressurePa / tKelvin) * (aZero + aOne*temp + aTwo*temp**2 + (bZero + bOne*temp)*xv + (cZero + cOne*temp)*xv**2) + \
        (pressurePa / tKelvin)**2 * (dZ + e*xv**2)

    airDensity = (pressurePa * ma / (z * r * tKelvin)) * (1 - xv * (1 - mv / ma)) * Decimal('0.001')
    return longdouble(airDensity)

    #Approximated air density:
    #es = 1.3146*10**9*exp(-5315.56/(t + 273.15))
    #airDensity = (0.46460 / (t + 273.15)) * (p - 0.0037960 * rh * es) * 10**-3
