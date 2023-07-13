## Overview
Hydrocron API is a new tool that implements functionalities that will allow 
hydrologists to have direct access to filtered data from our newest satellites. 
This innovative tool will provide an effortless way to filter data by feature ID, 
date range, polygonal area, and more. This data will be returned in formats such 
as CSV and geoJSON.

## Requirements
Python 3.10+

## Usage
Before starting the server you must first start a local database instance. The easiest method is to use docker

```
docker run --name hydrocrondb -e MYSQL_DATABASE=test -e MYSQL_ROOT_HOST='%' -e MYSQL_ROOT_PASSWORD=my-secret-pw -p 3306:3306 -v $(pwd)/mysql/20230601_test.sql:/docker-entrypoint-initdb.d/20230601_test.sql -d --rm mysql:latest
```

To run the server, please execute the following from the root directory:

```
python3 -m hydrocronapi
```

and open your browser to here:

```
http://localhost:8080/hydrocron/HydroAPI/1.0.0/ui/
```

Your Swagger definition lives here:

```
http://localhost:8080/hydrocron/HydroAPI/1.0.0/swagger.json
```

## Running with Docker

To run the server on a Docker container, please execute the following from the root directory:

```bash
# building the image
docker build -t hydrocronapi .

# starting up a container
docker run -p 8080:8080 hydrocronapi
```
