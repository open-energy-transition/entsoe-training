import pandas as pd

sensitivity = {}
for co2 in [150, 100, 50, 25, 0]:

    #######
    n.global_constraints.loc["CO2Limit", "constant"] = co2 * 1e6

    #######
    n.optimize(solver_name="highs", log_to_console=False)

    ### Aggregation step

    sensitivity[co2] = (
        pd.concat([n.statistics.capex(), n.statistics.opex()])
        .groupby("carrier")
        .sum()
        .div(1e9)
    )  # bn€/a

df = pd.DataFrame(sensitivity).T  # billion Euro/a
df.plot.area(
    stacked=True,
    linewidth=0,
    color=df.columns.map(n.carriers.color),
    figsize=(4, 4),
    xlim=(0, 150),
    xlabel=r"CO$_2$ emissions [Mt/a]",
    ylabel="System cost [bn€/a]",
    ylim=(0, 80),
    backend="matplotlib",
)
plt.legend(frameon=False, loc=(1.05, 0))
