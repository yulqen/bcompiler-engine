test:
	pytest --disable-warnings -m "not slow"

test_verbose:
	pytest -vv  --disable-warnings -m "not slow"

test_cov:
	pytest -vv --disable-warnings --cov 

test_stdout:
	pytest -vv --disable-warnings -s -m "not slow"

test_all:
	pytest --disable-warnings

test_no_logs:
	pytest -q -x --show-capture=no -m "not slow" --tb=short
