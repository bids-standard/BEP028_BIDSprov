coverage:
	pytest --cov-report term-missing --cov=bids_prov --cov-config=.coveragerc bids_prov

pytest:
	pytest bids_prov

clean:
	$(RM) -rf dist/ build/ *.egg-info
	$(RM) -rf **/__pycache__/
	$(RM) -rf __pycache__/
	$(RM) -rf .pytest_cache/
	$(RM) -rf .coverage
