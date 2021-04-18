# Rap quiz back
Backend of rap quiz, can be found [here](http://www.rapquiz.net/)

## Heroku commands

### Deploy

```
$ git add .
$ git commit -am "make it better"
$ git push heroku master
```

### Cancel current build
```
heroku builds:cancel
```

## Commands
- Create venv
```
python3 -m venv venv
```
- Install dependencies
```
pip install -r requirements.txt
```
- Store dependencies in `requirements.txt`
```
python -m pip freeze > requirements.txt
```
- Activate venv
```
source venv/bin/activate
```
- Set dev environment variables
```
. ./env_variables.sh
```
- Clean and format project
```
black app
autoflake --remove-all-unused-imports --ignore-init-module-imports --remove-unused-variables -i -r app
```

## Project structure

### Models

Regroup all models corresponding to the SQL tables (user,...).

### Routes

All clusters of routes of the application.

### Services

Regroup main functions of the application usually called by the blueprints.

### Shared

Shared variables and data accessible from different parts of the application.