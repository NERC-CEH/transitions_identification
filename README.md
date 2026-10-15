# Hydroclimatic Transition Event Identification

Python tool for identifying and characterising transitions between dry and wet hydrological and meteorological extremes using standardised indicators. The methods demonstrated in this repository are linked to the analyses presented in Historical and future transitions between opposing UK hydrological extremes ([Armitage et al., 2026](https://doi.org/10.5194/egusphere-2026-3154)), which uses threshold-based identification of consecutive dry and wet extremes to characterise hydroclimatic transition events. The workflow identifies transitions from a dry extreme to a wet extreme, or from a wet extreme to a dry extreme, and calculates the magnitude, duration, intensity and frequency of the identified transition events.

Schematic below demonstrates visually how the workflow identifies the extreme events and transitions. Extreme events over the given threshold (dashed grey line) comprising a transition are denoted by solid red markers, whilst extreme events discounted from transition identification are shown by hollow red markers. Shaded red periods represent a wet-dry transition and shaded blue periods a dry-wet transition.  

<img width="1465" height="727" alt="image" src="https://github.com/user-attachments/assets/4d1e3029-cf6a-46b7-bb70-179b1fb38d45" />


The repository demonstrates the workflow using and example catchment ([69007 - Mersey at Ashton Weir](https://nrfa.ceh.ac.uk/data/station/info/69007)) Standardised Streamflow Index (SSI) and Standardised Precipitation Index (SPI) data. The catchment is used to demonstrate how the transition-identification workflow can be applied consistently to streamflow (hydrological) and precipitation (meteorological) indicators. The dataset used here is the one model and one realisation for the future projections [enhanced future Flows and Groundwater (eFLaG) dataset](https://doi.org/10.5194/essd-15-2391-2023), with the standardised indicators [available here]([https://www.ceh.ac.uk/our-science/projects/eflag-enhanced-future-flows-and-groundwater](https://zenodo.org/records/23339444)). 

The same conceptual method demonstrated in this repo can applied to both indicators:

- **SSI transitions** represent transitions between `hydrological` dry and wet extremes in standardised streamflow.
- **SPI transitions** represent transitions between `meteorological` dry and wet extremes in standardised precipitation.

The attached script currently uses SSI-specific variable names, directory names and output filenames. To apply it to SPI, these elements should be generalised or replaced with the corresponding SPI names. The threshold definitions and transition metrics remain the same because both SSI and SPI are standardised indicators.

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
├── input_data/
    └── example_ssi_69007.csv
└── output_data/
    ├── example_ssi_69007_TransitionsEvents.csv
    └── example_ssi_69007_TransitionsSummary.csv
```

The exact folder structure can be adapted, but the input and output paths in the script must be updated accordingly.

## Requirements

The workflow requires Python 3 and can be installed using:

```bash
pip install -r requirements.txt
```
The script depends primarily on `pandas` and `pyextremes` packages.

## Input data

The transition-identification function expects a CSV file (with SPI or SSI) containing:

1. A monthly date column.
2. Standardised indicator accumulations (X1–X24).

In the current script, the date column is named Unnamed: 0; the date column contains monthly timestamps; accumulation columns follow the format X1, X3, X6, etc. The included examples use SSI data for NRFA catchment 69007 – Mersey at Ashton Weir.

## Configuration

Before running the script, update the input and output paths:

```python
inpath = 'input_data/'
outpath_t = 'output_data/'
```

For most users, no modification is required provided the input files are placed in the input_data/ directory.

Transition severity thresholds are defined as:
- Moderate = 1.0
- Severe = 1.6
- Extreme = 2.0
These thresholds are applied symmetrically to identify both wet and dry extremes.

## Running the transition extraction

The main function has the following form:

```python
extract_transitions(filename, threshold, acc=3)
```

### Parameters
- `filename` – Input SSI or SPI CSV file.
- `threshold` – One of Moderate, Severe, or Extreme.
- `acc` – Accumulation period (default = 3).

For example:

```python
extract_transitions(
    'example_ssi_69007.csv',
    'Moderate',
    acc=3
)
```
To run the script directly:
`python identify_characterise_transitions.py`

This example identifies `moderate` transitions using `SSI-3` for the selected catchment data.

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

### Station and flow-record information

Users should review the NRFA information for station 69007 before interpreting the SSI demonstration. The station record includes information about measurement changes and factors affecting runoff.

## Reproducibility

For reproducible analyses, record:

- indicator type, SSI or SPI;
- accumulation period;
- threshold classification;
- input dataset source and version;
- record start and end dates;
- missing-data treatment;
- Python version;
- package versions;
- date of analysis.

## Citation

If you use this repository, please cite the software using the citation information provided in the repository's `CITATION.cff` file or associated publication.

A suggested placeholder citation is:

```text
Armitage, R. (2026). Hydroclimatic transition event identification and
characterisation. GitHub repository.
```

Update this citation with the final repository URL, software version, DOI and contributor information when these become available.

## Authors and contributors

Original script author:

- Rachael Armitage

Additional contributors and maintainers should be listed here or in the repository metadata.

## Licence

This project is distributed under the terms of the GNU General Public License.

See the `LICENSE` file for the complete licence terms.

## Acknowledgements

The demonstration uses SSI and SPI data for NRFA station 69007, Mersey at Ashton Weir.

Station and catchment information are available from the UK National River Flow Archive:

[NRFA station 69007: Mersey at Ashton Weir](https://nrfa.ceh.ac.uk/data/station/info/69007)
