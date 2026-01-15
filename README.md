# logos-storage-nim-bin

[![codecov](https://codecov.io/github/nipsysdev/logos-storage-nim-bin/graph/badge.svg?token=DFKTDP7U9B)](https://codecov.io/github/nipsysdev/logos-storage-nim-bin)

Pre-built static libraries for [logos-storage-nim](https://github.com/logos-storage/logos-storage-nim).

## Supported Platforms

- **Linux x86_64** (`linux-amd64`)
- **Linux ARM64** (`linux-arm64`)

## Quick Start

Download the latest release from [GitHub Releases](https://github.com/nipsysdev/logos-storage-nim-bin/releases/latest).

Each release contains:

- `logos-storage-nim-<branch>-<commit>-<platform>.tar.gz` - Platform-specific archive
- `SHA256SUMS.txt` - Checksums for all archives

Extract and verify:

```bash
tar -xzf logos-storage-nim-master-60861d6a-linux-amd64.tar.gz
sha256sum -c SHA256SUMS.txt
```

The archive includes:

- `libstorage.a` - Main storage library
- `libnatpmp.a` - NAT-PMP library
- `libminiupnpc.a` - MiniUPnP library
- `libcircom_compat_ffi.a` - Circom compatibility library
- `libbacktrace.a` - Backtrace library
- `libleopard.a` - Leopard erasure coding library
- `libstorage.h` - Header file
- `SHA256SUMS.txt` - SHA256 checksums for all files

## Building from Source

### Prerequisites

- Python 3.14
- Git
- Make
- GCC
- ar

### Build

```bash
# Clone repository
git clone https://github.com/nipsysdev/logos-storage-nim-bin
cd logos-storage-nim-bin

# Build for host architecture
make build

# Build from specific branch
BRANCH="release/0.2.5" make build
```

### Make Targets

```bash
make build        # Build for host architecture
make clean        # Clean build artifacts
make clean-all    # Clean everything including dist/ and logos-storage-nim/
make ci-build     # Test build.yml workflow locally (requires act)
make ci-test      # Test test.yml workflow locally (requires act)
make ci-release   # Test release.yml workflow locally (requires act)
make help         # Show all targets
```

## Testing

```bash
# Install test dependencies
pip install -r requirements-test.txt

# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html
```

## CI/CD

- **Build**: Runs on push/PR to `main` branch
- **Release**: Scheduled at 00:00 UTC, creates releases when new commits are detected
- **Tests**: Runs on push/PR to `main` branch

## Versioning

Format: `<branch>-<commit-hash>`

Example: `master-60861d6a` means built from logos-storage-nim branch `master` at commit `60861d6a`.

## License

MIT - see [LICENSE](LICENSE) file.
