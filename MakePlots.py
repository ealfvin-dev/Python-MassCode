import matplotlib.pyplot as plt
from statistics import mean

def plotDeltas(deltas, sw):
    x_units = []
    tick_label = []

    for i in range(len(deltas)):
        x_units.append(i + 1)
        tick_label.append(str(i + 1))

    colors = []
    for s in deltas:
        diff = abs(s) / sw

        if(diff <= 1):
            r = diff * 0.9
            g = 0.7 + diff * 0.3
            b = 0.15 - diff * 0.1
            a = 0.9
        else:
            r = 0.9 + diff * 0.1
            g = 1 - (diff - 1)
            b = 0.05
            a = 0.9

        if(r > 1):
            r = 1
        if(g < 0):
            g = 0

        colors.append((r, g, b, a))

    fig, ax = plt.subplots()

    ax.bar(x_units, deltas, tick_label=tick_label,
            width=0.8, color=colors)

    ax.plot([0.5, len(deltas) + 0.5], [0, 0], "k-")
    dottedLine, = ax.plot([0.5, len(deltas) + 0.5], [sw, sw], "k:", label=chr(177) + ' ' + chr(963) + '$_w$' + " Accepted")
    ax.plot([0.5, len(deltas) + 0.5], [-1*sw, -1*sw], "k:")

    legend = fig.legend(handles=[dottedLine], loc='upper right')

    ax.set_xlabel('Observation')
    ax.set_ylabel('Delta (mg)')
    ax.set_title('Residuals (Deltas)')

    return fig

def plotSensitivities(sensitivities):
    x_units = []
    tick_label = []
    colors = []
    relativeSensitivities = []

    if(mean(sensitivities) < 5):
        relativeSensitivity = 1
    elif(mean(sensitivities) < 50):
        relativeSensitivity = 10
    elif(mean(sensitivities) < 500):
        relativeSensitivity = 100
    elif(mean(sensitivities) < 5000):
        relativeSensitivity = 1000
    elif(mean(sensitivities) < 50000):
        relativeSensitivity = 10000
    else:
        relativeSensitivity = 100000

    for i in range(len(sensitivities)):
        x_units.append(i + 1)
        tick_label.append(str(i + 1))
        colors.append((0.11, 0.45, 0.82, 0.92))
        relativeSensitivities.append(sensitivities[i] - relativeSensitivity)

    fig, ax = plt.subplots()

    ax.bar(x_units, relativeSensitivities, tick_label=tick_label,
            width=0.8, color=colors)

    ax.plot([0.5, len(relativeSensitivities) + 0.5], [0, 0], "k-")

    ax.set_xlabel('Observation')
    ax.set_ylabel('Sensitivity - ' + str(relativeSensitivity) + ' (mg/div)')
    ax.set_title('Sensitivities')

    return fig

def plotScatter(self, airDensities, deltas):
    pass