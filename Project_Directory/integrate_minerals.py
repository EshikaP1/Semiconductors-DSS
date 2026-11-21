"""Build an annual mineral dataset from USGS workbooks and cleaned CSVs.

Requires pandas and openpyxl. Example:
    python integrate_minerals.py --usgs-dir ~/Downloads --out-dir results

Add --annual-csv PATH for each cleaned file with one row per mineral and year.
"""

import argparse
from pathlib import Path

import pandas as pd


SOURCES = {
    "gallium": "ds140-gallium-2021.xlsx",
    "germanium": "ds140-germanum-2022.xlsx",
    "indium": "ds140-indium-2022.xlsx",
}
KEY = ["mineral", "year"]
FIELDS = {
    "Production": "us_production_kg",
    "Imports": "us_imports_kg",
    "Exports": "us_exports_kg",
    "Stocks": "us_stocks_kg",
    "Apparent consumption": "us_apparent_consumption_kg",
    "Unit value ($/t)": "us_nominal_unit_value_usd_per_kg",
    "Unit value (98$/t)": "us_real_unit_value_1998_usd_per_kg",
    "World production": "world_production_kg",
}


def read_usgs(path, mineral):
    raw = pd.read_excel(path, header=4, keep_default_na=False)
    raw.columns = raw.columns.str.strip()
    rows = raw.loc[raw["Year"].astype(str).str.fullmatch(r"[12]\d{3}")].copy()
    if rows.empty:
        raise ValueError(f"{path.name}: no annual observations found")
    clean = pd.DataFrame({"mineral": mineral, "year": rows["Year"].astype(int)})
    missing = []
    for source, target in FIELDS.items():
        values = rows[source].map(lambda value: str(value).strip())
        markers = values.isin(["", "NA", "W"])
        for index, marker in values[markers].items():
            missing.append((mineral, clean.at[index, "year"], target, marker or "blank"))
        numbers = pd.to_numeric(values.mask(markers), errors="raise")
        clean[target] = numbers / 1000 if source.startswith("Unit value") else numbers * 1000
    clean["source_file"] = path.name
    clean["source_row"] = rows.index + 6
    return clean, missing


def merge_annual(master, path):
    extra = pd.read_csv(path)
    extra["mineral"] = extra["mineral"].astype("string").str.strip().str.lower()
    years = extra["year"].astype("string").str.strip()
    if not years.str.fullmatch(r"[12]\d{3}").fillna(False).all():
        raise ValueError(f"{path.name}: year must contain four-digit observation years")
    extra["year"] = years.astype(int)
    invalid = ~extra["mineral"].isin(SOURCES)
    if invalid.any():
        raise ValueError(f"{path.name}: unexpected mineral names: {extra.loc[invalid, 'mineral'].unique().tolist()}")
    if extra.duplicated(KEY).any():
        raise ValueError(f"{path.name}: duplicate mineral-year rows. Summarize country-level records first.")
    overlap = sorted((set(master) & set(extra)) - set(KEY))
    if overlap:
        raise ValueError(f"{path.name}: overlapping columns need review: {', '.join(overlap)}")
    matches = master[KEY].merge(extra[KEY], how="outer", on=KEY, indicator=True)
    counts = matches["_merge"].value_counts()
    print(f"{path.name}: {counts['both']} matched, {counts['left_only']} master-only, {counts['right_only']} input-only")
    return master.merge(extra, how="left", on=KEY, validate="one_to_one")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--usgs-dir", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--annual-csv", type=Path, action="append", default=[])
    args = parser.parse_args()
    tables = []
    missing_values = []
    for mineral, filename in SOURCES.items():
        path = args.usgs_dir.expanduser() / filename
        if not path.is_file():
            print(f"Missing USGS workbook: {filename}")
            continue
        table, missing = read_usgs(path, mineral)
        tables.append(table)
        missing_values.extend(missing)
    if not tables:
        parser.error("No matching USGS workbooks found")
    master = pd.concat(tables, ignore_index=True)
    if master.duplicated(KEY).any():
        raise ValueError("Duplicate mineral-year rows in USGS data")
    for path in args.annual_csv:
        master = merge_annual(master, path.expanduser())
    master["mineral"] = master["mineral"].str.capitalize()
    out_dir = args.out_dir.expanduser()
    out_dir.mkdir(parents=True, exist_ok=True)
    master.sort_values(KEY).to_csv(out_dir / "master_dataset.csv", index=False)
    pd.DataFrame(
        missing_values, columns=[*KEY, "field", "source_marker"]
    ).assign(mineral=lambda frame: frame["mineral"].str.capitalize()).to_csv(
        out_dir / "missing_value_log.csv", index=False
    )
    print(f"Saved {len(master)} mineral-year rows to {out_dir / 'master_dataset.csv'}")


if __name__ == "__main__":
    main()
