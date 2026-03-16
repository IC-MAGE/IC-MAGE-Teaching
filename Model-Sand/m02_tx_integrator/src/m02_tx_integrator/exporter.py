from pathlib import Path

from m02_tx_integrator.results import IntegrationResult


class Exporter:
    @staticmethod
    def to_csv(
        result: IntegrationResult,
        output_dir: str | Path,
        filename_prefix: str = "M02_",
        clean: bool = False,
        index: bool = True,
    ) -> Path:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        file_path = output_path / f"{filename_prefix}{result.label}.csv"
        result.to_dataframe(clean=clean).to_csv(file_path, index=index)
        return file_path

    @staticmethod
    def to_csv_batch(
        results: list[IntegrationResult],
        output_dir: str | Path,
        filename_prefix: str = "M02_",
        clean: bool = False,
        index: bool = True,
    ) -> list[Path]:
        return [
            Exporter.to_csv(
                result=result,
                output_dir=output_dir,
                filename_prefix=filename_prefix,
                clean=clean,
                index=index,
            )
            for result in results
        ]