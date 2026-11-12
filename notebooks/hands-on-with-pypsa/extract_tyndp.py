"""Extract TYNDP 2026 NT+ 2035 hourly demand, capacity factors and installed capacities for DE, AT and CH.

Sources (identical files):
- ENTSO-E/ENTSOG TYNDP 2026 Scenarios data package, https://2026.entsos-tyndp-scenarios.eu/download/
- Open-TYNDP mirror, https://storage.googleapis.com/open-tyndp-data-store/2026/2026-11-11/inputs/
  (Demand.zip, PECD.zip, PEMMDB_2.X.zip)

Licence: ENTSO-E/ENTSOG TYNDP 2026 Scenarios data; terms on the download page.

Demand is the e-market electricity load (MW); capacity factors are PECD onshore wind,
offshore wind (DE only) and utility-scale solar PV (p.u.). All series use weather scenario WS032, which the
demand file maps to climate year SSP245_CMR5_2031; PECD columns carry the same WS labels.

Installed capacities (MW) come from the PEMMDB 2.X National Trends files, sheets "Wind" and
"Solar", rows "Onshore wind e-market", "Offshore wind e-market" (hub ready plus radial) and
"Photovoltaic e-market". They exclude shared-RES and dedicated H2 capacity and, for DE, the
rooftop PV that PEMMDB lists separately and that sits on the prosumer node.

Usage: python extract_tyndp.py PATH-TO-TYNDP-2026-PACKAGE  (needs pandas and openpyxl)
"""

import sys
from pathlib import Path

import pandas as pd

YEAR = 2035
WEATHER_SCENARIO = "WS032"
CLIMATE_YEAR = "SSP245_CMR5_2031"
ZONES = {"DE": "DE00", "AT": "AT00", "CH": "CH00"}
CARRIERS = {
    "DE": ["onwind", "offwind", "solar"],
    "AT": ["onwind", "solar"],
    "CH": ["onwind", "solar"],
}
ANNUAL_DEMAND_TWH = {"DE": 621.644, "AT": 77.316, "CH": 51.937}
PECD_FILES = {
    "onwind": "{zone}_CapacityFactors_Wind_Onshore_{year}.csv",
    "offwind": "{zone}_CapacityFactors_Wind_Offshore_{year}.csv",
    "solar": "Solar PV Utility {zone}.csv",
}
PEMMDB_ROWS = {
    "onwind": ("Wind", ["Installed capacities Onshore wind e-market (GW):"]),
    "offwind": (
        "Wind",
        [
            "Installed capacities Offshore wind e-market - hub ready (GW):",
            "Installed capacities Offshore wind e-market - radial (GW):",
        ],
    ),
    "solar": ("Solar", ["Installed capacities Photovoltaic e-market (GW):"]),
}
PEMMDB_TOTAL_ROWS = {
    "onwind": "Installed capacities Onshore wind Total(GW):",
    "offwind": "Installed capacities Offshore wind Total (GW):",
    "solar": "Installed capacities Photovoltaic (GW):",
}
EXPECTED_CAPACITY_MW = {
    "DE onwind": 156055,
    "DE offwind": 50089,
    "DE solar": 135941,
    "AT onwind": 10000,
    "AT solar": 20500,
    "CH onwind": 252,
    "CH solar": 580,
}
HOURS = 8760
DATA_DIR = Path(__file__).resolve().parent / "data"
OUTPUT = DATA_DIR / f"tyndp2026-nt{YEAR}-hourly-demand-wind-solar.csv"
OUTPUT_PEMMDB = DATA_DIR / f"tyndp2026-nt{YEAR}-wind-solar-capacity.csv"


def read_demand(package: Path, zone: str) -> pd.Series:
    path = package / "Demand" / "Demand" / str(YEAR) / f"ELECTRICITY_MARKET {YEAR}.xlsx"
    raw = pd.read_excel(path, sheet_name=zone, header=None, skiprows=9)
    climate_years, labels = raw.iloc[0], raw.iloc[1]
    col = labels[labels == WEATHER_SCENARIO].index.item()
    assert climate_years[col] == CLIMATE_YEAR, climate_years[col]
    series = raw.iloc[2:, col].astype(float).reset_index(drop=True)
    assert len(series) == HOURS and series.notna().all() and (series > 0).all(), zone
    return series


def read_capacity_factor(package: Path, zone: str, pattern: str) -> pd.Series:
    path = package / "PECD" / "PECD" / str(YEAR) / pattern.format(zone=zone, year=YEAR)
    raw = pd.read_csv(path, skiprows=10)
    series = raw[WEATHER_SCENARIO].astype(float)
    assert len(series) == HOURS and series.notna().all(), path
    assert series.between(0, 1).all(), path
    return series


def read_installed_capacity(package: Path, zone: str, carrier: str) -> float:
    """Installed capacity in MW of the e-market wind or utility PV of a PEMMDB zone."""
    path = (
        package
        / "PEMMDB_2.X"
        / "PEMMDB_2.X"
        / str(YEAR)
        / f"PEMMDB_{zone}_NationalTrends_{YEAR}.xlsx"
    )
    sheet, labels = PEMMDB_ROWS[carrier]
    raw = pd.read_excel(path, sheet_name=sheet, header=None, index_col=0, skiprows=7)[1]
    assert raw.index.is_unique and raw.index.notna().all(), path
    capacity = float(raw[labels].astype(float).sum())
    assert raw[PEMMDB_TOTAL_ROWS[carrier]] >= capacity > 0, path
    return capacity * 1e3


def write_pemmdb(package: Path) -> None:
    capacity = {
        f"{country} {carrier}": round(read_installed_capacity(package, zone, carrier))
        for country, zone in ZONES.items()
        for carrier in CARRIERS[country]
    }
    assert capacity == EXPECTED_CAPACITY_MW, capacity
    df = pd.Series(capacity, name="p_nom_max").rename_axis("generator").to_frame()
    df.to_csv(OUTPUT_PEMMDB)
    print(f"{OUTPUT_PEMMDB} ({OUTPUT_PEMMDB.stat().st_size} B)")
    print(df.to_string())


def main(package: Path) -> None:
    columns: dict[str, pd.Series] = {}
    for country, zone in ZONES.items():
        columns[f"{country} load"] = read_demand(package, zone).round(1)
        for carrier in CARRIERS[country]:
            columns[f"{country} {carrier}"] = read_capacity_factor(
                package, zone, PECD_FILES[carrier]
            ).round(4)

    df = pd.DataFrame(columns)
    df.index = pd.date_range(f"{YEAR}-01-01", periods=HOURS, freq="h", name="snapshot")
    for country, twh in ANNUAL_DEMAND_TWH.items():
        assert round(df[f"{country} load"].sum() / 1e6, 3) == twh, country

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT)
    print(f"{OUTPUT} ({OUTPUT.stat().st_size / 1e3:.0f} kB)")
    print(df.filter(like="load").sum().div(1e6).round(3).rename("TWh").to_string())
    print(
        df.drop(columns=df.filter(like="load").columns)
        .mean()
        .round(4)
        .rename("mean CF")
        .to_string()
    )
    write_pemmdb(package)


if __name__ == "__main__":
    main(Path(sys.argv[1]))
