#!/usr/bin/env python3
"""
Simple script to download the latest baksmali JAR from GitHub releases
"""

import os
import requests
import json
from pathlib import Path


def download_latest_baksmali():
    """Download the latest baksmali JAR from GitHub releases"""
    try:
        print("Fetching latest baksmali release information...")
        
        # Get latest release info from GitHub API
        response = requests.get("https://api.github.com/repos/JesusFreke/smali/releases/latest")
        response.raise_for_status()
        
        release_data = response.json()
        print(f"Latest release: {release_data['tag_name']}")
        
        # Find baksmali JAR asset
        baksmali_asset = None
        for asset in release_data.get('assets', []):
            if 'baksmali' in asset['name'].lower() and asset['name'].endswith('.jar'):
                baksmali_asset = asset
                break
        
        if not baksmali_asset:
            print("❌ No baksmali JAR found in latest release")
            return None
        
        # Download the file
        download_url = baksmali_asset['browser_download_url']
        filename = baksmali_asset['name']
        
        print(f"Downloading {filename}...")
        print(f"Download URL: {download_url}")
        
        response = requests.get(download_url, stream=True)
        response.raise_for_status()
        
        # Create tools directory
        tools_dir = Path("tools")
        tools_dir.mkdir(exist_ok=True)
        
        jar_path = tools_dir / filename
        
        # Download with progress
        total_size = int(response.headers.get('content-length', 0))
        downloaded = 0
        
        with open(jar_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total_size > 0:
                        progress = (downloaded / total_size) * 100
                        print(f"\rProgress: {progress:.1f}%", end='', flush=True)
        
        print(f"\n✅ Downloaded baksmali JAR: {jar_path.absolute()}")
        return str(jar_path.absolute())
        
    except requests.RequestException as e:
        print(f"❌ Network error: {e}")
        return None
    except Exception as e:
        print(f"❌ Error downloading baksmali: {e}")
        return None


if __name__ == "__main__":
    jar_path = download_latest_baksmali()
    if jar_path:
        print(f"\nBaksmali JAR is ready at: {jar_path}")
        print("\nYou can now use it in the GUI or command line:")
        print(f"  GUI: Select this file in the Baksmali JAR field")
        print(f"  CLI: --baksmali-jar {jar_path}")
    else:
        print("\n❌ Failed to download baksmali JAR")
        print("Please download manually from: https://github.com/JesusFreke/smali/releases")