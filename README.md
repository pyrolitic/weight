# weight
Matplotlib based weight/BMI graphing and extrapolation. Target granularity is 1 day, less frequent samples are linearly interpolated. The date format is malleable, as it uses [dateparser](https://pypi.org/project/dateparser/) so `August 14, 2015` is as valid as `4 aug 2015`, but for numeric months it uses day-month-year order (`4/8/2015`).

The natural uits are height in cm and weight kg. This makes plotting them along with BMI on one scale easy. Other units and scales TODO.

## Installation
`pip3 install [--user] -r requirements.txt`

The matplotlib dependency may be available from your package manager and might work better that way.

## Usage
`python3 weight.py [after <date>]

Edit `data.yaml` with your correct date of birth.
Append weighing results to the `samples` list as you go.