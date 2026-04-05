#!/usr/bin/env python3
"""Test Android build functionality."""

import os
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_android_build():
    """Test Android build with client-lite patches."""
    print("Testing Android build...")
    
    # Set environment variables for Android build
    os.environ["TARGET_PLATFORM"] = "android"
    android_ndk_path = os.path.expanduser("~/Android/Sdk/ndk/29.0.14206865")
    os.environ["ANDROID_NDK_ROOT"] = android_ndk_path
    os.environ["NDK_ROOT"] = android_ndk_path
    
    try:
        # Import after setting environment
        from repository import ensure_logos_storage_repo, reset_repository
        from artifacts import build_libstorage_android
        from utils import get_parallel_jobs
        
        # Get repository
        logos_storage_dir, commit_info = ensure_logos_storage_repo("master", None)
        print(f"Repository ready at: {logos_storage_dir}")
        print(f"Commit: {commit_info.commit_short}")
        
        # Reset to clean state
        reset_repository(logos_storage_dir)
        print("✓ Repository reset")
        
        # Build Android version
        jobs = get_parallel_jobs()
        patch_dir = Path("patches")
        
        build_libstorage_android(logos_storage_dir, jobs, patch_dir)
        print("✓ Android build succeeded")
        
    except Exception as e:
        print(f"✗ Android build failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = test_android_build()
    sys.exit(0 if success else 1)