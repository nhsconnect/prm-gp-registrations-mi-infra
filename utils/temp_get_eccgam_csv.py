import os
import zipfile
import tempfile
from utils.ods_files import NEW_GP_FILE_HEADERS
import requests
import pandas as pd
from tqdm import tqdm

# Constants — adjust for latest release
ODS_URL = "https://geoportal.statistics.gov.uk/datasets/nhs-england-sub-icb-locations-eccg-quarterly-change-files/explore?filters=eyJGaWxlIFR5cGUiOiJjc3YifQ%3D%3D"  # placeholder if using stable
ECCGAM_ZIP_URL = "https://files.digital.nhs.uk/assets/ods/current/eamendam.zip"  # Use actual download URL
FILENAME_INSIDE_ZIP = "eccgam.csv"

def download_file(url, output_path):
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        total_size = int(r.headers.get('content-length', 0))
        with open(output_path, 'wb') as f, tqdm(
            total=total_size, unit='B', unit_scale=True, desc="Downloading"
        ) as bar:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
                bar.update(len(chunk))

def extract_csv_from_zip(zip_path, target_filename):
    with zipfile.ZipFile(zip_path, 'r') as z:
        with z.open(target_filename) as f:
            df = pd.read_csv(f, header=None, names=NEW_GP_FILE_HEADERS)
    return df

def main():
    with tempfile.TemporaryDirectory() as tmpdir:
        zip_path = os.path.join(tmpdir, "eamendam.zip")
        print(f"[INFO] Downloading eccgam from: {ECCGAM_ZIP_URL}")
        download_file(ECCGAM_ZIP_URL, zip_path)

        print("[INFO] Extracting eccgam.csv...")
        df = extract_csv_from_zip(zip_path, FILENAME_INSIDE_ZIP)

        print(f"[INFO] Loaded {len(df)} records.")
        print(df.head())

        # Optional: save to local CSV or process
        df.to_csv("eccgam_processed.csv", index=False)
        print("[INFO] Saved to eccgam_processed.csv")

if __name__ == "__main__":
    main()
