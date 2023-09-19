=================
timeseriesSubset
=================

Get timeseries of features within a given spatial region


Parameters
----------

feature : string
    Data requested for Reach or Node or Lake

subsetpolygon : string  
    GEOJSON of the subset area. 
    Example: '{"features": [{"type": "Feature","geometry": {"coordinates": [[-95.6499095054704,50.323685647314554],[-95.3499095054704,50.323685647314554],[-95.3499095054704,50.19088502467528],[-95.6499095054704,50.19088502467528],[-95.6499095054704,50.323685647314554]],"type": "LineString"},"properties": {}}],"type": "FeatureCollection"}'

start_time : string  
    Start time of the timeseries  (i.e 2023-08-04T00:00:00Z)

end_time : string
    End time of the timeseries

output : string
    Format of the data returned. Must be one of ["csv", "geojson"]

fields : string
    The fields to return. Defaults to "feature_id, time_str, wse, geometry"



Returns
-------

CSV or GEOJSON file containing the data for all features within the subset area and time period.


Responses
---------

200 : OK

400 : The specified URL is invalid (does not exist)

404 : An entry with the specified region was not found

413 : Your query returns too much data