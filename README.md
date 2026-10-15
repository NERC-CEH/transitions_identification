# Hydroclimatic Transition Event Identification

Python tool for identifying and characterising transitions between dry and wet hydrological and meteorological extremes using standardised indicators. The methods demonstrated in this repository are linked to the analyses presented in Historical and future transitions between opposing UK hydrological extremes ([Armitage et al., 2026](https://doi.org/10.5194/egusphere-2026-3154)), which uses threshold-based identification of consecutive dry and wet extremes to characterise hydroclimatic transition events. The workflow identifies transitions from a dry extreme to a wet extreme, or from a wet extreme to a dry extreme, and calculates the magnitude, duration, intensity and frequency of the identified transition events.

**Citation:**
*Armitage R, Magee E, Chevuturi A, Chan W, Hannaford J (2026) Historical and future transitions between opposing UK hydrological extremes. [https://doi.org/10.5194/egusphere-2026-3154](https://doi.org/10.5194/egusphere-2026-3154).*

Schematic below demonstrates visually how the workflow identifies the extreme events and transitions. Extreme events over the given threshold (dashed grey line) comprising a transition are denoted by solid red markers, whilst extreme events discounted from transition identification are shown by hollow red markers. Shaded red periods represent a wet-dry transition and shaded blue periods a dry-wet transition.  

<img width="1465" height="727" alt="image" src="https://github.com/user-attachments/assets/4d1e3029-cf6a-46b7-bb70-179b1fb38d45" />

This repository provides a Python tool for identifying and characterising transitions between opposing dry and wet hydroclimatic extremes using standardised indicators: Standardised Streamflow Index (SSI) and Standardised Precipitation Index (SPI). The repository demonstrates the workflow using and example catchment ([69007 - Mersey at Ashton Weir](https://nrfa.ceh.ac.uk/data/station/info/69007)) with SSI data. The catchment is used to demonstrate how the transition-identification workflow can be applied consistently to streamflow (hydrological) and precipitation (meteorological) indicators. The dataset used here is the one model and one realisation for the future projections [enhanced future Flows and Groundwater (eFLaG) dataset](https://doi.org/10.5194/essd-15-2391-2023), with the standardised indicators [available here](https://zenodo.org/records/23339444). 


## Method overview

The `identifying_characterising_transitions.py` script identifies individual wet and dry extremes using a peaks-over-threshold approach implemented through the `pyextremes` package. Three severity thresholds are available:

| Classification | Standardised threshold |
|---|---:|
| Moderate | ±1.0 |
| Severe | ±1.6 |
| Extreme | ±2.0 |

Values above the positive threshold are classified as wet extremes, while values below the corresponding negative threshold are classified as dry extremes. After identifying the extremes, the script orders them chronologically. A transition is recorded when two consecutive extreme events have different states:

- `dry` followed by `wet`
- `wet` followed by `dry`

The transition starts at the last identified extreme of the initial state and ends at the first identified extreme of the opposite state.

## Transition characteristics

For each transition, the script records the following information:

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

The transition metrics are calculated as:

```text
Magnitude = |StartVal - EndVal|

Duration = EndDate - StartDate

Intensity = Magnitude / Duration
```

The transition frequency is reported as the number of identified transitions per decade:

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
├── data/
│   ├── SSI/
│   │   └── 69007/
│   │       └── SSI_example.csv
│   ├── SPI/
│   │   └── 69007/
│   │       └── SPI_example.csv
│   └── metadata/
│       └── catchment_metadata.csv
└── outputs/
    ├── SSI/
    └── SPI/
```

The exact folder structure can be adapted, but the input and output paths in the script must be updated accordingly.

## Requirements

The workflow requires Python 3 and can be installed using:

```bash
pip install -r requirements.txt
```

## Input data

The transition-identification function expects a CSV file (with SPI or SSI) containing:

1. A monthly date column.
2. Different columns of standardised indicator accumulations columns (X1 - X24). For example, `X3` represents a three-month accumulation period.

In the current script, the date column is read as `Unnamed: 0`, renamed to `MONTH`, and converted to a monthly datetime index.

## Configuration

Before running the script, update the input, output and metadata paths:

```python
inpath = "/path/to/input/data/"
outpath_t = "/path/to/outputs/TransitionEventsData/"
eflag_metadata_path = "/path/to/metadata/eflag_lat_long_full.csv"
```

The current implementation is configured for the eFLaG SSI dataset and includes the following hydrological models:

```python
models = ["GR4J", "GR6J", "PDM", "G2G"]
```

It also supports 12 regional climate model simulations:

```python
rcms = [
    "RCM1", "RCM2", "RCM3", "RCM4",
    "RCM5", "RCM6", "RCM7", "RCM8",
    "RCM9", "RCM10", "RCM11", "RCM12"
]
```

These model and simulation lists can be modified when applying the method to other datasets, including the demonstration SSI and SPI data for station 69007.

The output directories for each threshold and accumulation period must exist before the script is run. For example:

```text
outputs/
└── TransitionEventsData/
    ├── Moderate/
    │   └── SSI3/
    ├── Severe/
    │   └── SSI3/
    └── Extreme/
        └── SSI3/
```

## Running the transition extraction

The main function has the following form:

```python
extract_transitions(model, rcm, threshold, acc=3)
```

### Parameters

- `model`: Hydrological model name.
- `rcm`: Regional climate model simulation name.
- `threshold`: Transition severity classification. Accepted values are `Moderate`, `Severe` and `Extreme`.
- `acc`: Accumulation period of the standardised indicator. The default is `3`.

For example:

```python
extract_transitions(
    model="GR4J",
    rcm="RCM1",
    threshold="Moderate",
    acc=3
)
```

This example identifies moderate transitions using SSI-3 for the selected hydrological model and regional climate model simulation.

## Applying the method to SSI and SPI

The same conceptual method is applied to both indicators:

- **SSI transitions** represent changes between hydrological dry and wet extremes in standardised streamflow.
- **SPI transitions** represent changes between meteorological dry and wet extremes in standardised precipitation.

The attached script currently uses SSI-specific variable names, directory names and output filenames. To apply it to SPI, these elements should be generalised or replaced with the corresponding SPI names.

The threshold definitions and transition metrics remain the same because both SSI and SPI are standardised indicators.

## Outputs

### Event-level output

A separate CSV file is produced for each catchment, threshold, model, accumulation period and climate simulation combination.

The event-level output contains:

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

An example output filename is:

```text
Transitions_SSI3_Moderate_GR4J_69007.csv
```

### Summary output

The script also creates a summary CSV containing catchment-level transition characteristics:

```text
Station
Magnitude
Duration
Intensity
Frequency
Count
```

These fields represent:

- Mean transition magnitude
- Mean transition duration
- Mean transition intensity
- Transition frequency per decade
- Total number of transitions

Station metadata are joined to the summary output using the station identifier.

An example summary filename is:

```text
TransitionsSummary_SSI3_Moderate_GR4J_RCM1.csv
```

## Important considerations

### Consecutive extremes

A transition is identified only when consecutive events in the combined chronological sequence have different states. Multiple wet extremes followed by a dry extreme therefore produce a transition from the final wet extreme to the subsequent dry extreme.

### Duration

Duration is calculated in whole months. Because intensity is calculated as magnitude divided by duration, users should check for zero-duration transitions if applying the workflow to data with a temporal resolution finer than monthly.

### Input column names

The current script assumes that:

- The date column is named `Unnamed: 0`.
- Indicator columns use names such as `X3`.
- Input filenames follow the eFLaG naming convention.
- The station number can be extracted from a fixed part of the filename.

These assumptions may need to be changed for other datasets.

### Output directories

The script does not create missing output directories automatically. Required folders should therefore be created before execution.

### Station and flow-record information

Users applying the demonstration data should review the NRFA information for station 69007. The station record includes qualifications relating to high flows, measurement changes and the influence of reservoirs and flood-storage basins. These factors should be considered when interpreting streamflow-based extremes and transitions.

## Reproducibility

For reproducible use, record the following information alongside each analysis:

- Indicator used, such as SSI or SPI
- Accumulation period
- Threshold classification
- Input data source and version
- Record start and end dates
- Any missing-data treatment
- Hydrological model, where applicable
- Climate simulation, where applicable
- Python and package versions
- Date on which the analysis was run

## Citation

If you use this repository, please cite the software using the citation below:
```text
Armitage R, Magee E, Chevuturi A, Chan W, Hannaford J (2026) Hydroclimatic transition event identification and characterisation. GitHub repository link.
```

## Licence

This project is distributed under the terms of the GNU General Public License.

See the `LICENSE` file for the complete licence terms.

## Acknowledgements

The demonstration uses SSI and SPI data for NRFA station 69007, Mersey at Ashton Weir.

Station and catchment information are available from the UK National River Flow Archive:

[NRFA station 69007: Mersey at Ashton Weir](https://nrfa.ceh.ac.uk/data/station/info/69007)
