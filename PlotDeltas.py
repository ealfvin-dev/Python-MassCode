import matplotlib.pyplot as plt

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

    ax.plot([0.5, len(deltas) - 0.5], [0, 0], "k-")
    dottedLine, = ax.plot([0.5, len(deltas) - 0.5], [sw, sw], "k:", label="Accepted " + chr(177) + ' ' + chr(963) + '$_w$')
    ax.plot([0.5, len(deltas) - 0.5], [-1*sw, -1*sw], "k:")

    legend = plt.legend(handles=[dottedLine], loc='upper right')

    plt.xlabel('Observation')
    plt.ylabel('Delta (mg)')
    plt.title('Residuals (Deltas)')

    return plt.gcf()