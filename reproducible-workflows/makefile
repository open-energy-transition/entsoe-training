PYTHON = python

.PHONY: all clean

all: results/figure.png

results/figure.png: results/solved_cem.nc scripts/6_plot.py
	$(PYTHON) scripts/6_plot.py results/solved_cem.nc results/figure.png

results/solved_cem.nc: results/cem.nc scripts/5_solve.py
	$(PYTHON) scripts/5_solve.py results/cem.nc results/solved_cem.nc

results/cem.nc: data/costs.csv data/timeseries.csv data/tyndp2026-nt2035-wind-solar-capacity.csv scripts/4_build_model.py
	$(PYTHON) scripts/4_build_model.py

data/costs.csv: data/costs_2035.csv scripts/2_get_costs.py
	$(PYTHON) scripts/2_get_costs.py

data/timeseries.csv: data/tyndp2026-nt2035-hourly-demand-wind-solar.csv scripts/3_get_timeseries.py
	$(PYTHON) scripts/3_get_timeseries.py

data/costs_2035.csv data/tyndp2026-nt2035-hourly-demand-wind-solar.csv data/tyndp2026-nt2035-wind-solar-capacity.csv &: scripts/1_get_data.py
	$(PYTHON) scripts/1_get_data.py

clean:
	rm -f data/* results/*
