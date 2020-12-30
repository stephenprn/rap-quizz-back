# Skeleton-back
Skeleton universal project (back-end) including:
- OAuth2 authentication

## TODO
- leave room (delete userquiz relation)
- add in repo
- move to_json in endpoint or add option to not convert to json in service functions
- tags artists to get similar artist for false responses
- custom exceptions
- return types functions (->)
- typed dicts
- logger
- socket events enums

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