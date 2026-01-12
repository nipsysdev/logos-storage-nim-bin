.PHONY: help build clean clean-all test-ci test-release test-tests

build:
	python build.py

help:
	@echo "Available targets:"
	@echo "  make build       - Build for host architecture"
	@echo "  make clean       - Clean build artifacts (Nim cache, build directories, .o files)"
	@echo "  make clean-all   - Clean everything including dist/ and logos-storage-nim/"
	@echo "  make test-ci     - Test build.yml workflow locally (requires act)"
	@echo "  make test-tests  - Test test.yml workflow locally (requires act)"
	@echo "  make test-release- Test daily-release.yml workflow locally (requires act)"
	@echo "  make help        - Show this help message"

clean:
	python clean.py

clean-all:
	python clean.py --all

ci-build:
	act -W .github/workflows/build.yml push

ci-test:
	act -W .github/workflows/test.yml push

ci-release:
	act -W .github/workflows/daily-release.yml schedule
