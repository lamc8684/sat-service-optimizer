from typing import List
from pandas import DataFrame
import numpy as np
import logging


class MinFuelMaxRevenue():
    """
    Parent class with common patterns for optimizer algorithms
    """
    service_path: List[int] = []
    max_revenue: float = 0

    def __init__(self, service_options: DataFrame, fuel_reserve_kg: float):
        # initialize parameters for given servicing options and available fuel
        self.service_options: DataFrame = service_options
        self.fuel_costs: np.Array = self.service_options["fuel_cost"].to_numpy()
        self.revenues: np.Array = self.service_options["revenue"].to_numpy()
        self.fuel_reserve_kg: int = fuel_reserve_kg

    def optimize_path(self):
        """
        Leave this empty as it needs to be implemented by the child class
        """
        raise NotImplementedError()

    def __repr__(self) -> str:
        """
        Pretty printing for results from optimization
        """
        path_string = f"Maximum Revenue: ${self.max_revenue}\n"
        for i in range(0, len(self.service_path)):
            path_string+=f"{self.service_path[i]}"
            # if this is the last one, don't print the arrow
            if i != len(self.service_path) - 1 :
                path_string+="  ->  "
        return path_string


class GreedyLazyOptimizer(MinFuelMaxRevenue):
    """
    Greedy algoithm to find maximum revenue by ranking the options and picking the next best choice (not recurssive). Better for larger data sets but only approximate.
    This iteration is very lazy and only takes the maximum available where possible
    """

    def optimize_path(self) -> List[int]:
        """
        Find optimal path with greedy algorithm, return indeces of this path
        """
        # Create a copy of the data frame
        weighted_data_frame = self.service_options.copy()

        # Prevent divide-by-zero and handle NaN/infinite values
        weighted_data_frame["value_per_fuel_cost"] = weighted_data_frame["revenue"] / (
            weighted_data_frame["fuel_cost"].replace(0, float("inf"))
        )

        weighted_data_frame["original_index"] = weighted_data_frame.index

        # Remove any NaN or infinite values
        weighted_data_frame = weighted_data_frame.dropna().replace([float("inf"), -float("inf")], 0)

        # Sort data by highest value per fuel cost (greedy approach)
        weighted_service_options = weighted_data_frame.sort_values(
            by="value_per_fuel_cost", ascending=False
        ).reset_index(drop=True)

        available_fuel = self.fuel_reserve_kg
        max_revenue = 0

        for index in range(0, len(weighted_service_options)):
            if available_fuel - weighted_service_options.loc[index, "fuel_cost"] >= 0:
                self.service_path.append(weighted_service_options.loc[index, "original_index"])
                max_revenue += weighted_service_options.loc[index, "revenue"]
                available_fuel = available_fuel - weighted_service_options.loc[index, "fuel_cost"]

        self.max_revenue = max_revenue

        return self.service_path


class GreedyOptimizer(MinFuelMaxRevenue):
    """
    Greedy algoithm to find maximum revenue by ranking the options and picking the best choice (highest rank) with every iteration.
    """

    def optimize_path(self) -> List[int]:
        """
        Find optimal path with greedy algorithm, return indeces of this path
        """
        # create a copy of the data frame to store weighted revenue to fuel cost column
        weighted_data_frame = self.service_options.copy()
        weighted_data_frame["value_per_fuel_cost"] = weighted_data_frame["fuel_cost"] / weighted_data_frame["revenue"] 
        # sort this data frame by highest weight
        weighted_service_options = weighted_data_frame.sort_values(by="value_per_fuel_cost", ascending=False).reset_index(drop=True)

        # Recursive function for finding the next highest revenue per fuel cost within our fuel reserves
        def find_next_best(index: int, current_fuel_reserve: float, current_revenue: int, selected: List[int]):
            # If fuel reserve is exceeded, we're done with this path, return
            if current_fuel_reserve <= 0:
                return

            logging.debug(f"Index: {index}, Fuel: {current_fuel_reserve}, Revenue: {current_revenue}")
            
            # If we have considered all rows, we're done, update max revenue
            if index >= len(weighted_service_options):
                if current_revenue > self.max_revenue:
                    self.max_revenue = current_revenue
                    self.service_path = selected
                return

            # Try including the current row
            fuel_cost = weighted_service_options.loc[index, "fuel_cost"]
            if current_fuel_reserve - fuel_cost >= 0:
                selected.append(index)
                find_next_best(
                    index+1,
                    current_fuel_reserve - weighted_service_options.loc[index, "fuel_cost"],
                    current_revenue + weighted_service_options.loc[index, "revenue"],
                    selected,
                )

            # Try excluding the current row
            find_next_best(index + 1, current_fuel_reserve, current_revenue, selected)

        # Start finding path from first row

        selected = []

        find_next_best(index=0, current_fuel_reserve=self.fuel_reserve_kg, current_revenue=0, selected=selected)

        return self.service_path