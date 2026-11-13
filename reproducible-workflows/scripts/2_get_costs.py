"""Annualise investment costs

Uses a small utility function that calculates the **annuity** to annualise investment costs.
The annualised investment costs (`capital_cost` in PyPSA terms, €/MW/a)
The FOM cost is expressed as a percentage of the overnight investment cost per year,
and thus can be added to the annuity factor when calculating the annualised capital cost.

Before that, we apply the Open-TYNDP overwrites, based on TYNDP 2026 National Trends+ 2035.
"""

import os
import pandas as pd

from pypsa.costs import annuity


def main(input_data: pd.DataFrame) -> pd.DataFrame:

    costs = input_data

    # Convert units from kW to MW, the base unit of PyPSA
    costs.loc[costs.unit.str.contains("/kW"), "value"] *= 1e3
    costs.unit = costs.unit.str.replace("/kW", "/MW")

    defaults = {
        "FOM": 0,
        "VOM": 0,
        "efficiency": 1,
        "fuel": 0,
        "investment": 0,
        "CO2 intensity": 0,
        "discount rate": 0.07,
    }
    costs = costs.value.unstack().fillna(defaults)

    # Open-TYNDP overwrites, TYNDP 2026 National Trends+ 2035
    costs.loc["solar"] = costs.loc["solar-utility"]
    costs["lifetime"] = 25
    costs.loc["OCGT", ["fuel", "efficiency", "VOM", "CO2 intensity"]] = [33.93, 0.42, 1.6, 0.1744]
    costs.at["electrolysis", "efficiency"] = 0.7
    costs.loc["hydrogen storage underground", ["investment", "FOM"]] = [1750, 0]
    costs.loc[["onwind", "offwind", "solar"], "VOM"] = [0.015, 0.015, 0.01]

    costs["marginal_cost"] = costs["VOM"] + costs["fuel"] / costs["efficiency"]

    annuity_factor = annuity(costs["discount rate"], costs["lifetime"])

    costs["capital_cost"] = (annuity_factor + costs["FOM"] / 100) * costs["investment"]

    return costs


if __name__ == "__main__":

    input_path = os.path.join("data", "costs_2035.csv")
    output_path = os.path.join("data", "costs.csv")

    input_data = pd.read_csv(input_path, index_col=[0, 1])
    output_data = main(input_data)
    output_data.to_csv(output_path)
