import matplotlib.pyplot as plt

class DeltaPlot():
    def __init__(self, plotData):
        self.series = 1
        self.observations = []
        self.deltas = []
        self.sws = []

        self.setPlotData(plotData)

    def setPlotData(self, plotData):
        pass

    def plotDeltas(self):
        sw = 0.35

        x_units = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
        y_units = [0.1, 0.2, -0.3, -0.05, 0.7, -0.2, -0.1, 0.05, 0.3, 0.46, -0.3]

        colors = []
        for s in y_units:
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

        tick_label = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11']

        fig, ax = plt.subplots()

        ax.bar(x_units, y_units, tick_label=tick_label,
                width=0.8, color=colors)

        ax.plot([0.5, 11.5], [0, 0], "k-")
        dottedLine, = ax.plot([0.5, 11.5], [sw, sw], "k:", label=chr(177) + ' ' + chr(963) + '$_w$')
        ax.plot([0.5, 11.5], [-1*sw, -1*sw], "k:")

        legend = plt.legend(handles=[dottedLine], loc='upper right')

        plt.xlabel('Observation')
        plt.ylabel('Delta (mg)')
        plt.title('Residuals (Deltas)')

        return plt