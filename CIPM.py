from math import exp

def calculateAirDensity(t, p, rh):
    #Calculates the air density using the CIPM 2007 air density equation
    #Picard et al.: https://iopscience.iop.org/article/10.1088/0026-1394/45/2/004

    tKelvin = t + 273.15
    humidity = rh / 100.0
    pressurePa = p * (101325 / 760)

    a = 1.2378847*10**-5
    b = -1.9121316*10**-2
    c = 33.93711047
    d = -6.3431645*10**3

    alpha = 1.00062
    beta = 3.14*10**-8
    gamma = 5.6*10**-7

    r = 8.314472
    ma = 28.96546*10**-3
    mv = 18.01528*10**-3

    aZero = 1.58123*10**-6
    aOne = -2.9331*10**-8
    aTwo = 1.1043*10**-10
    bZero = 5.707*10**-6
    bOne = -2.051*10**-8
    cZero = 1.9898*10**-4
    cOne = -2.376*10**-6
    dZ = 1.83*10**-11
    e = -0.765*10**-8

    vaporPressure = exp(a * tKelvin**2 + b * tKelvin + c + d / tKelvin)
    f = alpha + beta * pressurePa + gamma * t**2
    xv = humidity * f * (vaporPressure / pressurePa)

    z = 1 - (pressurePa / tKelvin) * (aZero + aOne*t + aTwo*t**2 + (bZero + bOne*t)*xv + (cZero + cOne*t)*xv**2) + \
        (pressurePa / tKelvin)**2 * (dZ + e*xv**2)

    airDensity = (pressurePa * ma / (z * r * tKelvin)) * (1 - xv * (1 - mv / ma)) * 10**-3
    return airDensity

    #Approximated air density:
    #es = 1.3146*10**9*exp(-5315.56/(t + 273.15))
    #airDensity = (0.46460 / (t + 273.15)) * (p - 0.0037960 * rh * es) * 10**-3