import requests
import zipfile
import io
import os
from pathlib import Path

def download_comfy_frontend():
    print("Fetching latest release info...")
    try:
        resp = requests.get("https://api.github.com/repos/Comfy-Org/ComfyUI_frontend/releases/latest")
        resp.raise_for_status()
        data = resp.json()
        
        asset_url = None
        for asset in data.get("assets", []):
            if asset["name"] == "dist.zip":
                asset_url = asset["browser_download_url"]
                break
        
        if not asset_url:
            print("Error: dist.zip not found in latest release")
            return

        print(f"Downloading from {asset_url}...")
        r = requests.get(asset_url)
        r.raise_for_status()

        print("Extracting...")
        z = zipfile.ZipFile(io.BytesIO(r.content))
        
        target_dir = Path("backend/comfy_web")
        target_dir.mkdir(parents=True, exist_ok=True)
        
        z.extractall(target_dir)
        print(f"Success! Frontend extracted to {target_dir.absolute()}")
        
    except Exception as e:
        print(f"Failed: {e}")

if __name__ == "__main__":
    download_comfy_frontend()
