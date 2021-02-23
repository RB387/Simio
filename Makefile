fmt:
	black simio && black tests && pylint simio

test:
	pytest -vv

deploy:
	python setup.py sdist && twine upload dist/*