# Rule to run pytest with coverage and remove test_database.sqlite
test:
	pytest -vv --cov=../src/theThing .
	rm -f test_database.sqlite

clean:
	rm -f test_database.sqlite