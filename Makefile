.PHONY: help build clean clean-all ci-build ci-nightly ci-stable

build:
	python build.py

help:
	@echo "Available targets:"
	@echo "  make build      - Build for host architecture"
	@echo "  make clean      - Clean build artifacts (Nim cache, build directories, .o files)"
	@echo "  make clean-all  - Clean everything including dist/ and logos-storage-nim/"
	@echo "  make ci-build   - Test build.yml workflow locally (requires act)"
	@echo "  make ci-nightly - Test nightly-release.yml workflow locally (requires act)"
	@echo "  make ci-stable  - Test stable-release.yml workflow locally (requires act)"
	@echo "  make help       - Show this help message"

clean:
	python clean.py

clean-all:
	python clean.py --all

ci-build:
	act -W .github/workflows/build.yml push

ci-nightly:
	act -W .github/workflows/nightly-release.yml schedule

ci-stable:
	act -W .github/workflows/stable-release.yml schedule
