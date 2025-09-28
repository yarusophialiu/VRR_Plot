from pathlib import Path
import pandas as pd
import re


# Label mapping per scene + index (case-insensitive)
# SCENE_INDEX_TO_LABEL = {
#     "breakfastroom": {1: "Slow",   2: "Medium", 3: "Slow"},
#     "sibenik":       {1: "Fast",   2: "Fast",   3: "Medium"},
#     "salledebain":   {1: "Medium", 2: "Medium", 3: "Slow"},
#     "makeway":       {1: "Medium", 2: "Fast"},
#     "school":        {1: "Medium", 2: "Medium"},
#     "rogue":         {1: "Fast",   2: "Medium"},
# }

SCENE_INDEX_TO_LABEL = {
    "breakfastroom": {1: "Slow",   2: "Slow",   3: "Slow"},
    "salledebain":   {1: "Medium", 2: "Medium", 3: "Slow"},
    "school":        {1: "Medium", 2: "Slow"},
    "rogue":         {1: "Fast",   2: "Medium"},
    "makeway":       {1: "Medium", 2: "Fast"},
    "sibenik":       {1: "Fast",   2: "Fast",   3: "Fast"},
}


# Numeric value per label
LABEL_TO_VALUE = {"Slow": 1.0, "Medium": 1.5, "Fast": 2.0}

def add_bitrate_to_file(input_csv: Path, output_csv: Path):
    df = pd.read_csv(input_csv)
    df.columns = df.columns.str.strip()

    def extract_bitrate(speed: str):
        if pd.isna(speed):
            return None
        match = re.search(r'_(\d+)(?:\.(\d+))?mbps', speed)
        if not match:
            return None
        integer = int(match.group(1))
        fractional = int(match.group(2)) if match.group(2) else 0
        value_mbps = float(f"{integer}.{fractional}") if match.group(2) else integer
        return int(value_mbps * 1000)  # Mbps → kbps

    df["bitrate"] = df["speed"].apply(extract_bitrate)
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_csv, index=False)
    print(f"Processed: {input_csv.name} → {output_csv.name}")



def parse_scene_index_from_speed(speed_str: str):
    """
    Extract (scene, index) from strings like 'school2_1mbps' or 'sibenik3_4mbps'.
    Returns (scene_lower, index_int) or (None, None) if not matched.
    """
    if not isinstance(speed_str, str):
        return None, None
    s = speed_str.strip().lower()
    m = re.match(r'^([a-z_]+?)(\d+)_\d+(?:\.\d+)?mbps$', s)
    if not m:
        # Fallback: allow scene without underscore part (e.g., 'school2')
        m = re.match(r'^([a-z_]+?)(\d+)$', s)
        if not m:
            return None, None
    scene = m.group(1)
    idx = int(m.group(2))
    return scene, idx

def rewrite_speed_column(input_csv: Path, output_csv: Path):
    df = pd.read_csv(input_csv)
    df.columns = df.columns.str.strip()

    labels = []
    values = []

    for sp in df["speed"]:
        scene, idx = parse_scene_index_from_speed(sp)
        if scene in SCENE_INDEX_TO_LABEL and idx in SCENE_INDEX_TO_LABEL[scene]:
            label = SCENE_INDEX_TO_LABEL[scene][idx]
            value = LABEL_TO_VALUE[label]
        else:
            # Unknown pattern/scene/index — keep original as label, leave numeric empty
            label = None
            value = None
        labels.append(label)
        values.append(value)

    # Add label column (for transparency) and overwrite speed with numeric value
    df["speed_label"] = labels
    df["speed"] = values

    # Ensure output directory exists
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_csv, index=False)
    print(f"Rewrote speed for: {input_csv} → {output_csv}")


# process experiment results, rewrite bitrate and speed
# so that we can plot
if __name__ == "__main__":
    project_root = Path(__file__).resolve().parent.parent
    input_dir = project_root / "csv/experiment1_adaptive_streaming_0908/baseline"

    for csv_file in input_dir.glob("*.csv"):
        # Save alongside original with "filtered_" prefix
        output_file = csv_file.parent.parent / "processed_baseline" / f"{csv_file.name}"
        add_bitrate_to_file(csv_file, output_file)
        rewrite_speed_column(output_file, output_file)
        # break