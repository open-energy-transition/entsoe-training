PYTHON = python

.PHONY: all clean

all: results/figure.png

results/figure.png: results/solved_cem.nc scripts/plot_6.py
	$(PYTHON) scripts/plot_6.py results/solved_cem.nc results/figure.png

results/solved_cem.nc: results/cem.nc scripts/solve_5.py
	$(PYTHON) scripts/solve_5.py results/cem.nc results/solved_cem.nc

results/cem.nc: data/costs.csv data/timeseries.csv data/tyndp2026-nt2035-wind-solar-capacity.csv scripts/build_model_4.py
	$(PYTHON) scripts/build_model_4.py

data/costs.csv: data/costs_2035.csv scripts/get_costs_2.py
	$(PYTHON) scripts/get_costs_2.py

data/timeseries.csv: data/tyndp2026-nt2035-hourly-demand-wind-solar.csv scripts/get_timeseries_3.py
	$(PYTHON) scripts/get_timeseries_3.py

data/costs_2035.csv data/tyndp2026-nt2035-hourly-demand-wind-solar.csv data/tyndp2026-nt2035-wind-solar-capacity.csv &: scripts/get_data_1.py
	$(PYTHON) scripts/get_data_1.py

clean:
	rm -f data/* results/*
