# m02-tx-integrator

Installable Python library that refactors the standalone TXC M02/M09 integration script into an object-oriented API.

The original script remains untouched. This package exposes configurable parameter sets, test conditions, batch execution, DataFrame export, CSV export, and optional plotting helpers.

Example:

```python
from m02_tx_integrator import Exporter, TXCIntegrator, nevada_sand_original, reference_tests

material, stiffness = nevada_sand_original()
integrator = TXCIntegrator(material, stiffness)
results = integrator.run_batch(reference_tests()[:2])
Exporter.to_csv_batch(results, "outputs")
```