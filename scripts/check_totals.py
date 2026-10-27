"""Independent check of the Power BI figures, straight from the AEMO CSVs.

Recounts rows, duplicates and PERIODTYPE, then prints the financial-year
volume-weighted price, time-weighted price, interval count, negative-price share
and spike count, to compare with the DAX query output.

Usage: python scripts/check_totals.py data/aemo_price_demand
"""
import csv
import glob
import os
import sys
from collections import defaultdict
from datetime import datetime, timedelta

folder = sys.argv[1]
fy = defaultdict(lambda: [0.0, 0.0, 0.0, 0, 0, 0])  # price x demand, demand, price, n, negative, spike
seen = set()
duplicates = 0
period_types = set()

for path in glob.glob(os.path.join(folder, "*.csv")):
    with open(path, encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            period_types.add(row["PERIODTYPE"])
            # SETTLEMENTDATE is the end of the 5-minute interval
            start = datetime.strptime(row["SETTLEMENTDATE"], "%Y/%m/%d %H:%M:%S") - timedelta(minutes=5)
            key = (row["REGION"], start)
            duplicates += key in seen
            seen.add(key)
            price, demand = float(row["RRP"]), float(row["TOTALDEMAND"])
            y = start.year if start.month >= 7 else start.year - 1
            a = fy[f"FY{y}-{str(y + 1)[2:]}"]
            a[0] += price * demand
            a[1] += demand
            a[2] += price
            a[3] += 1
            a[4] += price < 0
            a[5] += price > 300

print("PERIODTYPE:", period_types, " duplicates:", duplicates, " rows:", len(seen))
for k in sorted(fy):
    a = fy[k]
    print(f"{k}  VWP {a[0] / a[1]:7.2f}  TWP {a[2] / a[3]:7.2f}  n {a[3]:7d}  neg {a[4] / a[3]:.3f}  spikes {a[5]}")
