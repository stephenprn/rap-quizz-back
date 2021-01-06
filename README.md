# Skeleton-back
Skeleton universal project (back-end) including:
- OAuth2 authentication

## TODO
- add in repo
- tags artists to get similar artist for false responses
- custom exceptions
- typed dicts
- logger
- socket events enums
- switch from uuid to url everywhere
- issue join hour quiz
- timer answer response (can be set when quiz created: no timer or timer limit)
- timeout connection socket to remove user from room
- utils request : convert param or abort

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

## Project structure

### Models

Regroup all models corresponding to the SQL tables (user,...).

### Routes

All clusters of routes of the application.

### Services

Regroup main functions of the application usually called by the blueprints.

### Shared

Shared variables and data accessible from different parts of the application.