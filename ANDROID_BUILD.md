# Android Build Configuration

This document explains the environment variables and configuration needed for building logos-storage-nim for Android.

## Environment Variables

### Required Variables

- `TARGET_PLATFORM=android` - Set this to enable Android cross-compilation
- `ANDROID_NDK_ROOT` or `NDK_ROOT` - Path to Android NDK (e.g., `~/Android/Sdk/ndk/29.0.14206865`)

### Optional Variables

- `NIMBLE_BIN` - Path to Nimble binary directory (default: `~/.nimble/bin`)
- `CHOSENIM_TOOLCHAINS` - Path to chosenim toolchains (default: `~/.choosenim/toolchains/nim-2.2.8/bin`)
- `SKIP_REPO_RESET` - Set to skip repository reset during build (useful for development)

## Setup

### 1. Install Android NDK

Download and install the Android NDK from the Android SDK Manager or from:

```
https://developer.android.com/ndk/downloads
```

### 2. Set Environment Variables

Add to your `~/.bashrc` or `~/.zshrc`:

```bash
export ANDROID_NDK_ROOT="$HOME/Android/Sdk/ndk/29.0.14206865"
export NIMBLE_BIN="$HOME/.nimble/bin"
export CHOSENIM_TOOLCHAINS="$HOME/.choosenim/toolchains/nim-2.2.8/bin"
```

### 3. Build

Use the main Python build script with Android target:
```bash
export TARGET_PLATFORM=android
python build.py
```

## Client-Lite Configuration

The Android build uses a "client-lite" configuration that:

- Uses SQLite for storage (no LevelDB)
- Excludes REST API functionality
- Optimizes for mobile deployment
- Reduces binary size and attack surface

## Troubleshooting

### NDK Not Found
```
ValueError: Android NDK not found at /path/to/ndk
```
Solution: Ensure `ANDROID_NDK_ROOT` points to a valid NDK installation.

### Missing Tools
```
ValueError: Android tool not found: /path/to/tool
```
Solution: Verify the NDK version and architecture match your system.

### Build Failures
If the build fails, try:
1. Clean the build directory: `rm -rf logos-storage-nim/build`
2. Reset the repository: `git submodule foreach --recursive git reset --hard HEAD`
3. Rebuild with verbose output: `export VERBOSITY=1`

### Patch Application Issues
The build system uses `git apply` instead of the `patch` command, which is more universally available. If you see patch-related errors, ensure:
- Git is properly installed and available
- The patch files are in the correct format
- You're in the correct directory when applying patches

## Architecture

The Android build targets ARM64 (aarch64) by default. This provides the best compatibility with modern Android devices.

The build process:
1. Initializes git submodules
2. Applies client-lite patches
3. Configures Android NDK toolchain
4. Cross-compiles with static linking
5. Generates `libstorage.a` for Android