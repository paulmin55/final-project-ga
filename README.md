# final-project-ga

Queries [SpaceX API](https://api.spacexdata.com/v3/launches) for historical flight details by:
* __flight number__
* __mission name__

## Getting Started
### Requirements
* python3

### Getting Started
#### Running the application
```
$ pip install -r requirements.txt
$ python -m flask run
```

#### Running on docker
```
$ docker build . -t <repo>/<image_name>:<tag>
$ docker run --rm -dp 5000:5000 <repo>/<image_name>:<tag>
```

#### URL
* index: [localhost:5000](localhost:5000)
* search by `flight number`: [localhost:5000/flight](localhost:5000/flight)
* search by `mission name`: [localhost:5000/mission](localhost:5000/mission)

