test:
	pytest

venv:
	source env/bin/activate

server:
	flask run --host 0.0.0.0 -p 5000

scrapalbums:
	python3 scraping/rapgenius/spiders/albums_spider.py

compose:
	docker-compose up -d

format:
	black app && autopep8 --in-place --aggressive --aggressive --recursive ./app