import typer
from typing import Optional
from pathlib import Path
from enum import Enum
import pandas as pd

from source.optimizer import GreedyLazyOptimizer, GreedyOptimizer


class OptimizerAlgorithm(str, Enum):
    GREEDY_LAZY = "greedy_lazy"
    GREEDY = "greedy" ## This one either has a recursion bug or needs to be parallelized
    

app = typer.Typer()

@app.command(help="Find optimized revenue path")
def optimize(
    data_path: Optional[Path] = 'data/servicing_options.csv',
    maximum_fuel_capacity_kg: Optional[int] = 20,
    optimizer_algorithm: Optional[OptimizerAlgorithm] = OptimizerAlgorithm.GREEDY.value,
):
    # read in the csv
    service_data = pd.read_csv(data_path)
    # pair the selected algorithm
    optimizer_map = {
        OptimizerAlgorithm.GREEDY_LAZY: GreedyLazyOptimizer,
        OptimizerAlgorithm.GREEDY: GreedyOptimizer
    }

    # initialize the class
    optimizer = optimizer_map[optimizer_algorithm](service_data, maximum_fuel_capacity_kg)
    # optimize and print the result
    optimizer.optimize_path()
    print(optimizer)
    return


if __name__ == "__main__":
    app()