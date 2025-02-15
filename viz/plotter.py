
import json
import os
import tempfile
import subprocess
import sys

import spats_shape_seq


class Plotter(object):

    def __init__(self):
        self._spats_path = os.path.normpath(os.path.join(os.path.dirname(spats_shape_seq.__file__), ".."))
        self.processes = []

    def stop(self):
        for proc in self.processes:
            if proc.returncode is None:
                proc.kill()

    def submit_plot(self, data, filename = ''):
        self.submit_plots([data], filename)

    def submit_plots(self, data, filename = ''):
        temp_file = tempfile.NamedTemporaryFile(delete = False)
        temp_file.write(json.dumps([data, filename]))
        # /usr/bin/python is force the native interpreter for mac
        # easy hack to avoid https://trello.com/c/azoPpIn3/135-viz-bug-cannot-change-filename-of-row-column-plot-file
        # (caused by anaconda, xref https://stackoverflow.com/questions/3692928/why-doesnt-the-save-button-work-on-a-matplotlib-plot )
        proc = subprocess.Popen(["/usr/bin/python", "viz/plotter.py", temp_file.name], cwd = self._spats_path)
        self.processes.append(proc)

    def _show_plot(self, figinfo):
        import matplotlib as mpl
        import matplotlib.pyplot as plt

        plt.figure(1)

        idx = 0
        fig = figinfo[0]
        filename = figinfo[1]
        n = len(fig)
        for res in fig:

            idx += 1
            plt.subplot(int("{}1{}".format(n, idx)))

            for plot in res["data"]:
                if "cmap" in plot:
                    name, val = plot["cmap"].split('_')
                    cmap = mpl.cm.ScalarMappable(norm = mpl.colors.Normalize(vmin = 0.0, vmax = 1.0), cmap = plt.get_cmap(name))
                    plt.plot(plot["x"], plot["y"], plot["m"], color = cmap.to_rgba(float(val)))
                elif "color" in plot:
                    plt.plot(plot["x"], plot["y"], plot["m"], color = plot["color"])
                else:
                    plt.plot(plot["x"], plot["y"], plot["m"])

            if "xlim" in res:
                plt.xlim(res["xlim"])
            else:
                plt.xlim(0, max(plot["x"]))

            if "ylim" in res:
                plt.ylim(res["ylim"])

            plt.legend([ p.get("label", "") for p in res["data"] ])
            plt.title(res["type"])
            plt.xlabel(res["x_axis"])
            plt.ylabel(res["y_axis"])

        plt.gcf().set_tight_layout(True)

        #def onclick(event):
        #    plt.close()
        #cid = plt.gcf().canvas.mpl_connect('button_press_event', onclick)

        if filename:
            plt.gcf().canvas.get_default_filename = lambda: "{}.png".format(filename)

        plt.show()

def show_plot(data_file):
    plot_data = json.loads(open(data_file, 'rb').read())
    Plotter()._show_plot(plot_data)

if __name__ == '__main__':
    show_plot(sys.argv[1])
