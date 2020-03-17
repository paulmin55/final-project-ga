# final-project-ga

Queries [SpaceX API](https://api.spacexdata.com/v3/launches) for historical flight details by:
* __flight number__
* __mission name__

## Getting Started
### Requirements
* python3

### Running the application
```
$ pip install -r requirements.txt
$ python -m flask run
```

### Running on docker
```
$ docker build . -t <repo>/<image_name>:<tag>
$ docker run --rm -dp 5000:5000 <repo>/<image_name>:<tag>
```

### URL
* index: [localhost:5000](http://localhost:5000)
* search by `flight number`: [localhost:5000/flight](http://localhost:5000/flight)
* search by `mission name`: [localhost:5000/mission](http://localhost:5000/mission)

### Notes
* App will use an example SpaceX API JSON dump file [spacex_launch_data.json](spacex_launch_data.json) in case there's no network connectivity.
