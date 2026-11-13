echo "Getting data"
python scripts/1_get_data.py
echo "Getting costs"
python scripts/2_get_costs.py
echo "Getting timeseries"
python scripts/3_get_timeseries.py
echo "Building model"
python scripts/4_build_model.py
echo "Solving"
python scripts/5_solve.py results/cem.nc results/solved_cem.nc
echo "Plotting"
python scripts/6_plot.py results/solved_cem.nc results/figure.png
