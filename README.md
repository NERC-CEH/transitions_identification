# Hydroclimatic Transition Event Identification

Python tool for identifying and characterising transitions between dry and wet hydrological and meteorological extremes using standardised indicators. The methods demonstrated in this repository are linked to the analyses presented in Historical and future transitions between opposing UK hydrological extremes ([Armitage et al., 2026](https://doi.org/10.5194/egusphere-2026-3154)), which uses threshold-based identification of consecutive dry and wet extremes to characterise hydroclimatic transition events. The workflow identifies transitions from a dry extreme to a wet extreme, or from a wet extreme to a dry extreme, and calculates the magnitude, duration, intensity and frequency of the identified transition events.

Schematic below demonstrates visually how the workflow identifies the extreme events and transitions. Extreme events over the given threshold (dashed grey line) comprising a transition are denoted by solid red markers, whilst extreme events discounted from transition identification are shown by hollow red markers. Shaded red periods represent a wet-dry transition and shaded blue periods a dry-wet transition.  

<img width="1465" height="727" alt="image" src="https://github.com/user-attachments/assets/4d1e3029-cf6a-46b7-bb70-179b1fb38d45" />

This repository provides a Python tool for identifying and characterising transitions between opposing dry and wet hydroclimatic extremes using standardised indicators: Standardised Streamflow Index (SSI) and Standardised Precipitation Index (SPI). 

- **SSI transitions** represent `transitions` between *hydrological* dry and wet extremes in standardised streamflow.
- **SPI transitions** represent `transitions` between *meteorological* dry and wet extremes in standardised precipitation.


The repository demonstrates the workflow using and example catchment ([69007 - Mersey at Ashton Weir](https://nrfa.ceh.ac.uk/data/station/info/69007)) with SSI data. The catchment is used to demonstrate how the transition-identification workflow can be applied consistently to streamflow (hydrological) and precipitation (meteorological) indicators. The dataset used here is the one model and one realisation for the future projections [enhanced future Flows and Groundwater (eFLaG) dataset](https://doi.org/10.5194/essd-15-2391-2023), with the standardised indicators [available here](https://zenodo.org/records/23339444). 


## Method overview

The script identifies individual wet and dry extremes using a peaks-over-threshold approach implemented through the `pyextremes` package.

Three severity thresholds are available:

| Classification | Standardised threshold |
|---|---:|
| Moderate | ±1.0 |
| Severe | ±1.6 |
| Extreme | ±2.0 |

Values above the positive threshold are classified as wet extremes, while values below the corresponding negative threshold are classified as dry extremes.

After identifying the extremes, the script orders them chronologically. A transition is recorded when two consecutive extreme events have opposing states:

- dry followed by wet
- wet followed by dry

The transition starts at the last identified extreme of the initial state and ends at the first identified extreme of the opposite state.

## Transition characteristics

For each identified transition, the script records:

| Variable | Description |
|---|---|
| `StartDates` | Date of the initial wet or dry extreme |
| `EndDates` | Date of the first following extreme of the opposite state |
| `StartState` | Initial state of the transition: `wet` or `dry` |
| `StartVal` | Standardised indicator value at the start |
| `EndVal` | Standardised indicator value at the end |
| `Magnitude` | Absolute difference between the start and end values |
| `Duration` | Number of months between the start and end dates |
| `Intensity` | Transition magnitude divided by duration |

The metrics are calculated as:

```text
Magnitude = |StartVal - EndVal|
Duration = EndDate - StartDate
Intensity = Magnitude / Duration
```

Transition frequency is calculated as the number of identified transitions per decade:

```text
Frequency = Number of transitions / Record length in decades
```

## Repository structure

```text
.
├── README.md
├── LICENSE
├── requirements.txt
├── identify_characterise_transitions.py
├── input_data/
│   ├── example_ssi_69007.csv
│   ├── example_spi_69007.csv
│   └── eflag_lat_long_69007.csv
└── output_data/
```

The script expects input files in the `input_data/` directory and writes outputs to the `output_data/` directory.

## Requirements

The workflow requires Python 3. Install the required packages using:

```bash
pip install -r requirements.txt
```

The script depends primarily on:

- `pandas`
- `pyextremes`

## Input data

## Input data

The transition-identification function expects a CSV file containing either SSI or SPI values with:

1. A monthly date column.
2. Columns containing standardised indicator values for different accumulation periods.

The accumulation columns should follow the naming convention `X1`, `X3`, `X6`, and so on. For example, `X3` represents a three-month accumulation period. The current script assumes that:

- the date column is named `Unnamed: 0`;
- the date column contains monthly timestamps;
- the accumulation columns follow the format `X1`, `X3`, `X6`, etc.

The script renames `Unnamed: 0` to `MONTH` and converts it to a datetime index.

## Configuration

The default paths are:

```python
inpath = 'input_data/'
outpath_t = 'output_data/'
```
No changes are required if the input files are stored in `input_data/` and the `output_data/` directory already exists.

The transition thresholds are defined in the script as:

```python
Moderate = 1
Severe = 1.6
Extreme = 2
```

These thresholds are applied symmetrically to identify wet and dry extremes.

## Running the transition extraction

The main function is:

```python
extract_transitions(filename, threshold, acc=3)
```

### Parameters

- `filename`: Name of the input SSI or SPI CSV file located in `input_data/`.
- `threshold`: Transition severity classification. Accepted values are `Moderate`, `Severe`, and `Extreme`.
- `acc`: Accumulation period of the standardised indicator. The default is `3`.
The filename, threshold, and accumulation period can be changed as required.

The script includes an example function call at the end. It can therefore be run directly using:

```bash
python identify_characterise_transitions.py
```

This example identifies moderate transitions using SSI-3 values from `example_ssi_69007.csv`.

## Outputs

The script writes two CSV files to the `output_data/` directory for each run.

### Event-level output

The event-level filename follows this format:

```text
<input_filename>_TransitionsEvents.csv
```

For example:

```text
example_ssi_69007_TransitionsEvents.csv
```

It contains:

```text
StartDates
EndDates
StartState
StartVal
EndVal
Magnitude
Duration
Intensity
```

### Summary output

The summary filename follows this format:

```text
<input_filename>_TransitionsSummary.csv
```

For example:

```text
example_ssi_69007_TransitionsSummary.csv
```

It contains:

```text
Magnitude
Duration
Intensity
Frequency
Count
```

The summary fields represent:

- `Magnitude`: mean transition magnitude
- `Duration`: mean transition duration in months
- `Intensity`: mean transition intensity
- `Frequency`: number of transitions per decade
- `Count`: total number of transitions identified

## Important considerations

### Consecutive extremes

A transition is recorded when two consecutive extreme events in the chronological event sequence have opposite states. Consecutive extremes of the same type do not form a transition.

### Duration and intensity

Duration is calculated in whole months between the start and end extreme events. Intensity is calculated by dividing magnitude by duration.

The workflow is intended for monthly data. Users adapting the script to other temporal resolutions should check the duration calculation and guard against zero-duration transitions.

### Input format

The script currently assumes:

- monthly data;
- a date column named `Unnamed: 0`;
- accumulation columns named `X1`, `X3`, `X6`, etc.;
- the requested accumulation column is present in the input file.

Alternative formats require corresponding changes to the data-import section.

### Output directory

The `output_data/` directory must exist before running the script because the current implementation does not create it automatically.

## Citation

If you use this repository, please cite the associated study:

```text
Armitage R, Magee E, Chevuturi A, Chan W, Hannaford J (2026) Historical and future transitions between opposing UK hydrological extremes. HESS, [https://doi.org/10.5194/egusphere-2026-3154](https://doi.org/10.5194/egusphere-2026-3154).
```

## Licence

This project is distributed under the terms of the GNU General Public License.

See the `LICENSE` file for the complete licence terms.

## Acknowledgements

This research was funded by the Natural Environment Research Council CANARI project (NE/W004984/1), and the CoCentre for Climate + Biodiversity + Water programme (NE/Y006496/1) funded by Science Foundation Ireland (SFI), Northern
Ireland’s Department of Agriculture, Environment and Rural Affairs (DAERA) and UK Research and Innovation (UKRI).
