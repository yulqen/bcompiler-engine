test:
	pytest -vv --disable-warnings

test_cov:
	pytest -vv --disable-warnings --cov .

test_stdout:
	pytest -vv --disable-warnings -s

