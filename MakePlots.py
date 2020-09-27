import matplotlib.pyplot as plt
from statistics import mean

def plotDeltas(deltas, sw, fontSize):
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

    legend = fig.legend(handles=[dottedLine], loc='upper right', fontsize=int(fontSize * 0.85))

    ax.set_xlabel('Observation', fontsize=fontSize)
    ax.set_ylabel('Delta (mg)', fontsize=fontSize)
    ax.set_title('Residuals (Deltas)', fontsize=fontSize)

    return fig

def plotSensitivities(sensitivities, fontSize):
    x_units = []
    tick_label = []
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
        relativeSensitivities.append(sensitivities[i] - relativeSensitivity)

    fig, ax = plt.subplots()

    ax.bar(x_units, relativeSensitivities, tick_label=tick_label,
            width=0.8, color=(0.11, 0.45, 0.82, 0.90))

    ax.plot([0.5, len(relativeSensitivities) + 0.5], [0, 0], "k-")

    ax.set_xlabel('Observation', fontsize=fontSize)
    ax.set_ylabel('Sensitivity - ' + str(relativeSensitivity) + ' (mg/div)', fontsize=fontSize)
    ax.set_title('Sensitivities', fontsize=fontSize)

    return fig

def plotScatter(sensitivities, deltas, temperatures, fontSize, dotSize):
    colors = []
    absDeltas = []

    tMax = max(temperatures)
    tMin = min(temperatures)
    tRange = tMax - tMin

    for i in range(len(deltas)):
        absDeltas.append(abs(deltas[i]))
        if(tRange == 0):
            colors.append((0.10, 0.25, 0.82, 0.92))
            continue

        if(temperatures[i] <= (tMin + tMax) / 2):
            r = 0.01 + 0.91 * (temperatures[i] - tMin) / (tRange / 2)
            g = 0.15
            b = 0.92

            colors.append((r, g, b, 0.92))
        else:
            r = 0.92
            g = 0.15
            b = 0.92 - 0.91 * (temperatures[i] - ((tMax + tMin) / 2)) / (tRange / 2)

            colors.append((r, g, b, 0.92))

    fig, ax = plt.subplots()

    ax.scatter(sensitivities, absDeltas, c=colors, s=dotSize, alpha=0.9)

    ax.set_xlabel('Sensitivity (mg/div)', fontsize=fontSize)
    ax.set_ylabel('abs(Delta) (mg)', fontsize=fontSize)
    ax.set_title('Sensitivity vs abs(Delta) vs Temp', fontsize=fontSize)

    senMin = min(sensitivities)
    senMax = max(sensitivities)
    senRange = senMax - senMin
    if(senRange == 0):
        senRange = 0.001

    dMin = min(absDeltas)
    dMax = max(absDeltas)
    dRange = dMax - dMin
    if(dRange == 0):
        dRange = 0.001

    ax.set_xlim(senMin - senRange / 2.3, senMax + senRange / 2.3)
    ax.set_ylim(dMin - dRange / 2.3, dMax + dRange / 2.3)

    return fig

def closeFigures():
    plt.close(fig='all')