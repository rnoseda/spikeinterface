import numpy as np

from .base import BaseWidget, to_attr
from .utils import get_unit_colors

from ..core import ChannelSparsity
from ..core.waveform_extractor import WaveformExtractor
from ..core.basesorting import BaseSorting


class StudyRunTimesWidget(BaseWidget):
    """
    Plot sorter run times for a GroundTruthStudy


    Parameters
    ----------
    study: GroundTruthStudy
        A study object.
    case_keys: list or None
        A selection of cases to plot, if None, then all.

    """

    def __init__(
        self,
        study,
        case_keys=None,
        backend=None,
        **backend_kwargs,
    ):
        if case_keys is None:
            case_keys = list(study.cases.keys())

        plot_data = dict(
            study=study,
            run_times=study.get_run_times(case_keys),
            case_keys=case_keys,
        )

        BaseWidget.__init__(self, plot_data, backend=backend, **backend_kwargs)

    def plot_matplotlib(self, data_plot, **backend_kwargs):
        import matplotlib.pyplot as plt
        from .utils_matplotlib import make_mpl_figure

        dp = to_attr(data_plot)

        self.figure, self.axes, self.ax = make_mpl_figure(**backend_kwargs)

        for i, key in enumerate(dp.case_keys):
            label = dp.study.cases[key]["label"]
            rt = dp.run_times.loc[key]
            self.ax.bar(i, rt, width=0.8, label=label)

        self.ax.legend()


# TODO : plot optionally average on some levels using group by
class StudyUnitCountsWidget(BaseWidget):
    """
    Plot unit counts for a study: "num_well_detected", "num_false_positive", "num_redundant", "num_overmerged"


    Parameters
    ----------
    study: GroundTruthStudy
        A study object.
    case_keys: list or None
        A selection of cases to plot, if None, then all.

    """

    def __init__(
        self,
        study,
        case_keys=None,
        backend=None,
        **backend_kwargs,
    ):
        if case_keys is None:
            case_keys = list(study.cases.keys())

        plot_data = dict(
            study=study,
            count_units=study.get_count_units(case_keys=case_keys),
            case_keys=case_keys,
        )

        BaseWidget.__init__(self, plot_data, backend=backend, **backend_kwargs)

    def plot_matplotlib(self, data_plot, **backend_kwargs):
        import matplotlib.pyplot as plt
        from .utils_matplotlib import make_mpl_figure
        from .utils import get_some_colors

        dp = to_attr(data_plot)

        self.figure, self.axes, self.ax = make_mpl_figure(**backend_kwargs)

        columns = dp.count_units.columns.tolist()
        columns.remove("num_gt")
        columns.remove("num_sorter")

        ncol = len(columns)

        colors = get_some_colors(columns, color_engine="auto", map_name="hot")
        colors["num_well_detected"] = "green"

        xticklabels = []
        for i, key in enumerate(dp.case_keys):
            for c, col in enumerate(columns):
                x = i + 1 + c / (ncol + 1)
                y = dp.count_units.loc[key, col]
                if not "well_detected" in col:
                    y = -y

                if i == 0:
                    label = col.replace("num_", "").replace("_", " ").title()
                else:
                    label = None

                self.ax.bar([x], [y], width=1 / (ncol + 2), label=label, color=colors[col])

            xticklabels.append(dp.study.cases[key]["label"])

        self.ax.set_xticks(np.arange(len(dp.case_keys)) + 1)
        self.ax.set_xticklabels(xticklabels)
        self.ax.legend()


# TODO : plot optionally average on some levels using group by
class StudyPerformances(BaseWidget):
    """
    Plot performances over case for a study.


    Parameters
    ----------
    study: GroundTruthStudy
        A study object.
    mode: str
        Which mode in "swarm"
    case_keys: list or None
        A selection of cases to plot, if None, then all.

    """

    def __init__(
        self,
        study,
        mode="swarm",
        performance_names=("accuracy", "precision", "recall"),
        case_keys=None,
        backend=None,
        **backend_kwargs,
    ):
        if case_keys is None:
            case_keys = list(study.cases.keys())

        plot_data = dict(
            study=study,
            perfs=study.get_performance_by_unit(case_keys=case_keys),
            mode=mode,
            performance_names=performance_names,
            case_keys=case_keys,
        )

        BaseWidget.__init__(self, plot_data, backend=backend, **backend_kwargs)

    def plot_matplotlib(self, data_plot, **backend_kwargs):
        import matplotlib.pyplot as plt
        from .utils_matplotlib import make_mpl_figure
        from .utils import get_some_colors

        import pandas as pd
        import seaborn as sns

        dp = to_attr(data_plot)
        perfs = dp.perfs
        study = dp.study

        if dp.mode in ("ordered", "snr"):
            backend_kwargs["num_axes"] = len(dp.performance_names)
        self.figure, self.axes, self.ax = make_mpl_figure(**backend_kwargs)

        if dp.mode == "ordered":
            for count, performance_name in enumerate(dp.performance_names):
                ax = self.axes.flatten()[count]
                for key in dp.case_keys:
                    label = study.cases[key]["label"]

                    val = perfs.xs(key).loc[:, performance_name].values
                    val = np.sort(val)[::-1]
                    ax.plot(val, label=label)
                ax.set_title(performance_name)
                if count == 0:
                    ax.legend()

        elif dp.mode == "snr":

            metric_name = dp.mode
            for count, performance_name in enumerate(dp.performance_names):
                ax = self.axes.flatten()[count]

                max_metric = 0
                for key in dp.case_keys:
                    x = study.get_metrics(key).loc[:, metric_name].values
                    y = perfs.xs(key).loc[:, performance_name].values
                    label = study.cases[key]["label"]
                    ax.scatter(x, y, label=label)
                    max_metric = max(max_metric, np.max(x))
                ax.set_title(performance_name)
                ax.set_xlim(0, max_metric * 1.05)
                ax.set_ylim(0, 1.05)
                if count == 0:
                    ax.legend()


        elif dp.mode == "swarm":
            levels = perfs.index.names
            df = pd.melt(
                perfs.reset_index(),
                id_vars=levels,
                var_name="Metric",
                value_name="Score",
                value_vars=dp.performance_names,
            )
            df["x"] = df.apply(lambda r: " ".join([r[col] for col in levels]), axis=1)
            sns.swarmplot(data=df, x="x", y="Score", hue="Metric", dodge=True)
            

