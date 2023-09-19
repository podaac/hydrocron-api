# Overview

Hydrocron has two main API endpoints:
- [timeseries/](/timeseries) which returns all of the timesteps for a single feature ID, and
- [timeseriesSubset/](/subset) which returns all of the timesteps for all of the features within a given GeoJSON polygon.

## Limitations

Character limits in URL?

Data size return limits?

## Feature ID

The main timeseries endpoint allows users to search by feature ID.

River reach and node ID numbers are defined in the [SWOT River Database (SWORD)](https://doi.org/10.1029/2021WR030054),
and can be browsed using the [SWORD Explorer Interactive Dashboard](https://www.swordexplorer.com/).

Lake ID numbers are defined in the SWOT Lake Prior Database.

SWOT may observe lakes and rivers that do not have an ID in the prior databases. In those cases, hydrology features are added to the Unassigned Lakes data product.
Hydrocron does not currently support Unassigned rivers and lakes.
