PYTHON = python

.PHONY: all clean

all: results/figure.png

results/figure.png: results/cem_solved.nc scripts/plot.py
	$(PYTHON) scripts/plot.py results/cem_solved.nc results/figure.png

results/cem_solved.nc: results/cem.nc scripts/solve.py
	$(PYTHON) scripts/solve.py results/cem.nc results/cem_solved.nc

results/cem.nc: data/costs.csv data/timeseries.csv scripts/build_model.py
	$(PYTHON) scripts/build_model.py

data/costs.csv: data/costs_2030.csv scripts/get_costs.py
	$(PYTHON) scripts/get_costs.py

data/timeseries.csv: data/time-series-lecture-2.csv scripts/get_timeseries.py
	$(PYTHON) scripts/get_timeseries.py

data/costs_2030.csv data/time-series-lecture-2.csv &: scripts/get_data.py
	$(PYTHON) scripts/get_data.py

clean:
	rm -f data/* results/*
