# Rule to run pytest with coverage and remove test_database.sqlite
test:
	pytest -vv --cov=.. .
	rm -f ../src/*.sqlite

# Rule to remove all .sqlite files
clean:
	rm -f ../src/database_la_cosa