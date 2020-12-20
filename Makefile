test:
	pytest

venv:
	source env/bin/activate

server:
	flask run --host 0.0.0.0 -p 5000