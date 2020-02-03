#!/usr/bin/env python3

import re
import sys
from datetime import datetime
from collections import namedtuple

import dateparser
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.lines
from scipy.interpolate import interp1d as interp
import numpy as np
import yaml

DATA_FILE = "data.yaml"
Datum = namedtuple("Datum", ["date", "age", "weight", "height", "bmi"])

UNIT_PATTERN = re.compile(r"(\d+(?:\.\d*)?|\.\d+)\s*(\w*)")
FT_IN_PATTERN = re.compile(r"(\d+)\s*(?:f|ft|foot|feet)\s*(\d+)\s*(?:i|in|inch|inches|inchs)?", re.I)

def parse_unit(rec):
    m = UNIT_PATTERN.match(rec)
    if not m:
        raise ValueError
    return m.groups()

def parse_feet_inches(rec):
    m = FT_IN_PATTERN.match(rec)
    if not m:
        raise ValueError
    return m.groups()

def parse_samples(samples, dob):
    data = []
    for sample in samples:
        print(sample)
        dateStr = sample['date']
        weightStr = sample['weight']
        heightStr = sample['height']
        
        d = dateparser.parse(dateStr, settings={'DATE_ORDER': 'DMY'})
        try:
            weight, wu = parse_unit(weightStr)
            if wu == 'kg':
                weight *= 0.453592
            else:
                print("warning: bad weight unit, expected kg or lb")
        except ValueError:
            print("error: bad weight record '%s'" % weightStr)
            continue
        
        try:
            height, hu = parse_unit(heightStr)
            if hu != 'cm':
                print("warning: bad height unit, expected cm or in")
        except ValueError:
            try:
                ft, inc = parse_feet_inches(heightStr)
                height = ft * 0.3048 + inc * 0.0254
            except ValueError:
                print("error: bad height record '%s'" % weightStr)
                continue
        
        delta = (d - dob)
        w = float(weight)
        h = float(height)
        bmi = w / (h/100)**2
        age = delta.total_seconds() / (365.2425 * 24 * 3600)
        age = int(age * 10) / 10.0
        data.append(Datum(d, age, w, h, bmi))
    return data

def main():
    with open(DATA_FILE, "r") as stream:
        root = yaml.safe_load(stream)
        dob = dateparser.parse(root['DOB'])
        data = parse_samples(root['samples'], dob)

    after = dob
    if len(sys.argv) > 1 and sys.argv[1].lower() == "after":
        after = dateparser.parse(' '.join(sys.argv[2:]))
        
    data = list(filter(lambda datum: datum.date >= after, data))

    #ax = plt.twiny()
    #TODO: interpolate dates
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)

    maxy = int(max([max(d.weight, d.height, d.bmi) for d in data]) + 10)
    ax.set_yticks(list(range(0, maxy, 10)))
    ax.set_yticks(list(range(0, maxy, 5)), minor=True)

    interpolate = True
    if interpolate:
        ords = [x.date.toordinal() for x in data]
        fine = list(range(min(ords), max(ords)+1, 1))
        kind = "linear"
        #kind = "quadratic"
        height_interp = interp(ords, [x.height for x in data], kind=kind, fill_value="extrapolate")
        weight_interp = interp(ords, [x.weight for x in data], kind=kind, fill_value="extrapolate")
        wfit = np.polyfit(ords, [x.weight for x in data], 1)
        bfit = np.polyfit(ords, [x.weight / (x.height/100)**2 for x in data], 1)
        print("wfit:", wfit, "ords:", ords)
        #weight_interp = np.poly1d(wfit)

        hs = height_interp(fine)
        ws = weight_interp(fine)
        bms = ws / ((hs/100) ** 2)
        dws = np.diff(ws)
        dws = np.append(dws, dws[-1])
        dws = -dws * 100

        dates = [datetime.fromordinal(f) for f in fine]
        ax.plot_date(dates, hs, 'b-', label="Height in cm")
        ax.plot_date(dates, ws, 'r-', label="Weight in kg")
        ax.plot_date(dates, bms, 'g-', label="BMI")
        ax.plot_date(dates, dws, '-', label="-dW/d(decagrams per day)")

        #best fit 1d
        ords.append(ords[-1] + 100)
        ax.plot(ords, np.poly1d(wfit)(ords))
        ax.plot(ords, np.poly1d(bfit)(ords))

    else:
        #age
        xs = list(range(50))
        xt = [datetime(1995+i, 5, 24) for i in xs]
        #ax.set_xticks(xt, map(str, xs))

        #ax_age, ax_date = twiny();
        #x.set_xlabel("Age")

    #plots
    dates = [d.date for d in data]
    ax.plot_date(dates, [d.height for d in data], 'b.')
    ax.plot_date(dates, [d.weight for d in data], 'r.')
    ax.plot_date(dates, [d.bmi for d in data], 'g.')

    #yticks
    ax.grid(True, which="major", axis="y", ls="-", lw=1.0)
    ax.grid(True, which="minor", axis="y", ls="--", lw=0.5)

    #xticks
    years = mdates.YearLocator()
    months = mdates.MonthLocator()
    #ym_fmt = mdates.DateFormatter('%Y')
    month_fmt = mdates.DateFormatter('%b/%Y')
    ax.xaxis.set_major_locator(years)
    ax.xaxis.set_major_formatter(month_fmt)
    ax.xaxis.set_minor_locator(months)
    #ax.xaxis.set_minor_formatter(month_fmt)
    ax.grid(True, which="major", axis="x", ls="-", c="black", lw=1.5)
    ax.grid(True, which="minor", axis="x", ls="--", lw=0.5)

    #today
    today_x = matplotlib.dates.date2num(datetime.now())
    today = matplotlib.lines.Line2D([today_x, today_x], [-10, maxy], c="purple")
    ax.add_line(today)

    #bmi ranges
    bounds = [15, 18.5, 25, 30, 40, 50]
    cols = ["purple", "green", "yellow", "orange", "red"]
    for s, e, c in zip(bounds, bounds[1:], cols):
        ax.axhspan(s, e, color=c, alpha=0.4)

    ax.legend()
    plt.show()

if __name__ == "__main__":
    main()
