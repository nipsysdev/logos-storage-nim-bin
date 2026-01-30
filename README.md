# logos-storage-nim-bin

[![codecov](https://codecov.io/github/nipsysdev/logos-storage-nim-bin/graph/badge.svg?token=DFKTDP7U9B)](https://codecov.io/github/nipsysdev/logos-storage-nim-bin)

Pre-built static libraries for [logos-storage-nim](https://github.com/logos-storage/logos-storage-nim).

## Why Use logos-storage-nim-bin?

While the upstream [logos-storage-nim](https://github.com/logos-storage/logos-storage-nim) provides stable dynamic libraries (`.so`, `.dylib`, `.dll`), this repository offers **static libraries** (`.a`) with key advantages:

- **Simplified Integration**: No need to manage dynamic library paths or runtime loading—just link against the `.a` files
- **No Runtime Dependencies**: All dependencies (libnatpmp, libminiupnpc, libbacktrace) are bundled
- **Maximum Compatibility**: Built with architecture-specific flags for broad CPU support
- **Complete Bundle**: Includes all 4 required static libraries in one package

## Release Types

This repository provides two types of releases:

### Stable Releases

- **Trigger**: Builds from upstream tagged releases (e.g., v0.2.5)
- **Purpose**: Production-ready builds
- **Tag Format**: Same as upstream tags

### Nightly Pre-releases

- **Trigger**: Daily builds from upstream master branch commits
- **Purpose**: Latest development builds
- **Tag Format**: `master-{commit_short}`

## Supported Platforms

### Linux

- **x86_64 (amd64)**: `linux-amd64`
- **ARM64 (aarch64)**: `linux-arm64`

### macOS

- **Apple Silicon (ARM64)**: `darwin-arm64`

### Windows

- **x86_64 (amd64)**: `windows-amd64`

## Quick Start

Download the latest stable release from [GitHub Releases](https://github.com/nipsysdev/logos-storage-nim-bin/releases/latest).

Each release contains:

- `logos-storage-nim-<tag>-<platform>.tar.gz` - Platform-specific archive (stable releases)
- `logos-storage-nim-<branch>-<commit>-<platform>.tar.gz` - Platform-specific archive (nightly releases)
- `SHA256SUMS.txt` - Checksums for all archives

Extract and verify:

```bash
# Stable release example
tar -xzf logos-storage-nim-v0.2.5-linux-amd64.tar.gz
sha256sum -c SHA256SUMS.txt

# Nightly release example
tar -xzf logos-storage-nim-master-60861d6a-linux-amd64.tar.gz
sha256sum -c SHA256SUMS.txt
```

The archive includes:

- `libstorage.a` - Main storage library
- `libnatpmp.a` - NAT-PMP library
- `libminiupnpc.a` - MiniUPnP library
- `libbacktrace.a` - Backtrace library
- `libstorage.h` - Header file
- `SHA256SUMS.txt` - SHA256 checksums for all files

## Building from Source

### Prerequisites

- Python 3.14
- Git
- Make
- GCC
- ar

**Windows**: Install MSYS2 from https://www.msys2.org/ and install required packages:

```bash
pacman -S --needed base-devel mingw-w64-x86_64-gcc mingw-w64-x86_64-cmake mingw-w64-x86_64-make git
```

### Build

```bash
# Clone repository
git clone https://github.com/nipsysdev/logos-storage-nim-bin
cd logos-storage-nim-bin

# Build for host architecture (default: master branch)
make build

# Build from specific branch
BRANCH="release/0.2.5" make build

# Build from specific commit
COMMIT="abc123def456789abc123def456789abc123def" make build

# Build from specific tag
TAG="v0.2.5" make build
```

**Note**: `BRANCH`, `COMMIT`, and `TAG` are mutually exclusive. Specify only one.

### Make Targets

```bash
make build        # Build for host architecture
make clean        # Clean build artifacts
make clean-all    # Clean everything including dist/ and logos-storage-nim/
make ci-build     # Test build.yml workflow locally (requires act)
make ci-nightly   # Test nightly-release.yml workflow locally (requires act)
make ci-stable    # Test stable-release.yml workflow locally (requires act)
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

- **Build**: Runs on push to `main` and on any PRs
- **Nightly Release**: Runs daily at 00:00 UTC and on push to main. Creates pre-releases for new upstream commits
- **Stable Release**: Runs daily at 00:00 UTC and on push to main. Creates releases for new upstream tags
- **Stable Refresh**: Checks daily and refreshes stable releases older than 89 days

## Versioning

### Nightly Releases

Format: `<branch>-<commit-hash>`

Example: `master-60861d6a` means built from logos-storage-nim branch `master` at commit `60861d6a`.

### Stable Releases

Format: `<tag>`

Example: `v0.2.5` means built from logos-storage-nim tag `v0.2.5`.

## License

MIT - see [LICENSE](LICENSE) file.
