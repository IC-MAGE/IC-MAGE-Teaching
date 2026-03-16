from collections.abc import Iterable

from m02_tx_integrator.results import IntegrationResult


class Plotter:
    @staticmethod
    def plot_stress_path(results: Iterable[IntegrationResult], ax=None):
        plt = Plotter._import_pyplot()
        axis = ax or plt.subplots()[1]
        for result in results:
            axis.plot(result.p, result.q, label=result.label)
        axis.set_xlabel("p")
        axis.set_ylabel("q")
        axis.legend()
        return axis

    @staticmethod
    def plot_stress_strain(results: Iterable[IntegrationResult], ax=None):
        plt = Plotter._import_pyplot()
        axis = ax or plt.subplots()[1]
        for result in results:
            axis.plot(result.eax, result.q, label=result.label)
        axis.set_xlabel("eax (%)")
        axis.set_ylabel("q")
        axis.legend()
        return axis

    @staticmethod
    def plot_volumetric(results: Iterable[IntegrationResult], ax=None):
        plt = Plotter._import_pyplot()
        axis = ax or plt.subplots()[1]
        for result in results:
            axis.plot(result.eax, result.evol, label=result.label)
        axis.set_xlabel("eax (%)")
        axis.set_ylabel("evol (%)")
        axis.legend()
        return axis

    @staticmethod
    def _import_pyplot():
        try:
            import matplotlib.pyplot as plt
        except ImportError as exc:
            raise ImportError("matplotlib is required for plotting. Install m02-tx-integrator[plots].") from exc
        return plt