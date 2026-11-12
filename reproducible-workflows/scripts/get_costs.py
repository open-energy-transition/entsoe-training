"""Annualise investment costs

Uses a small utility function that calculates the **annuity** to annualise investment costs.
The annualised investment costs (`capital_cost` in PyPSA terms, €/MW/a)
The FOM cost is expressed as a percentage of the overnight investment cost per year,
and thus can be added to the annuity factor when calculating the annualised capital cost:
"""

import os
import pandas as pd

from pypsa.costs import annuity


def main(input_data: pd.DataFrame) -> pd.DataFrame:

    costs = input_data

    defaults = {
        "FOM": 0,
        "VOM": 0,
        "efficiency": 1,
        "fuel": 0,
        "investment": 0,
        "lifetime": 25,
        "CO2 intensity": 0,
        "discount rate": 0.07,
    }
    costs = costs.value.unstack().fillna(defaults)

    costs.at["OCGT", "fuel"] = costs.at["gas", "fuel"]
    costs.at["CCGT", "fuel"] = costs.at["gas", "fuel"]
    costs.at["OCGT", "CO2 intensity"] = costs.at["gas", "CO2 intensity"]
    costs.at["CCGT", "CO2 intensity"] = costs.at["gas", "CO2 intensity"]
    costs["marginal_cost"] = costs["VOM"] + costs["fuel"] / costs["efficiency"]

    annuity_factor = annuity(costs["discount rate"], costs["lifetime"])

    costs["capital_cost"] = (annuity_factor + costs["FOM"] / 100) * costs["investment"]

    return costs


if __name__ == "__main__":

    input_path = os.path.join("data", "costs_2030.csv")
    output_path = os.path.join("data", "costs.csv")

    input_data = pd.read_csv(input_path, index_col=[0, 1])
    output_data = main(input_data)
    output_data.to_csv(output_path)
