import os
from pathlib import Path

def remove_small_csvs(folder: str, min_lines: int = 5):
    folder_path = Path(folder)
    if not folder_path.exists():
        print(f"Folder not found: {folder_path}")
        return

    removed = 0
    checked = 0

    for csv_path in folder_path.glob("*.csv"):
        print(f'csv_path {csv_path}')
        checked += 1
        try:
            # Count non-empty lines to be robust against trailing blanks
            with csv_path.open("r", encoding="utf-8", errors="ignore") as f:
                line_count = sum(1 for line in f if line.strip())

            if line_count < min_lines:
                csv_path.unlink()  # delete the file
                removed += 1
                print(f"Removed {csv_path} (non-empty lines: {line_count})")
            else:
                print(f"Kept    {csv_path} (non-empty lines: {line_count})")

        except Exception as e:
            print(f"Error processing {csv_path}: {e}")

    print(f"\nDone. Checked: {checked}, Removed: {removed}, Kept: {checked - removed}")


# remove csv file with < 5 lines
if __name__ == "__main__":
    # change this if your CSV folder has a different path/name
    project_root = Path(__file__).resolve().parent.parent   # go up from utils/
    csv_folder = project_root / "csv" / "experiment1_adaptive_streaming_0908"
    remove_small_csvs(csv_folder, min_lines=5)
