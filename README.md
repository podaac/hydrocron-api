## Overview
Hydrocron API is a new tool that implements functionalities that will allow 
hydrologists to have direct access to filtered data from our newest satellites. 
This innovative tool will provide an effortless way to filter data by feature ID, 
date range, polygonal area, and more. This data will be returned in formats such 
as CSV and geoJSON.

## Requirements
Python 3.10+

## Usage
To run the server, please execute the following from the root directory:

```
pip3 install -r requirements.txt
python3 -m podaac
```

and open your browser to here:

```
http://localhost:8080/hydrocron/HydroAPI/1.0.0/ui/
```

Your Swagger definition lives here:

```
http://localhost:8080/hydrocron/HydroAPI/1.0.0/swagger.json
```

To launch the integration tests, use tox:
```
sudo pip install tox
tox
```

## Running with Docker

To run the server on a Docker container, please execute the following from the root directory:

```bash
# building the image
docker build -t podaac .

# starting up a container
docker run -p 8080:8080 podaac
```