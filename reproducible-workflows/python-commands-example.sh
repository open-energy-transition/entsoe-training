echo "Getting data"
python scripts/get_data_1.py
echo "Getting costs"
python scripts/get_costs_2.py
echo "Getting timeseries"
python scripts/get_timeseries_3.py
echo "Building model"
python scripts/build_model_4.py
echo "Solving"
python scripts/solve_5.py results/cem.nc results/solved_cem.nc
echo "Plotting"
python scripts/plot_6.py results/solved_cem.nc results/figure.png
