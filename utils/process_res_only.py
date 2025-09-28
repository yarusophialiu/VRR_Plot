import re
import pandas as pd
from pathlib import Path


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



def parse_scene_index(s: str):
    """Extract (scene, index) from 'salledebain2' etc."""
    if not isinstance(s, str):
        return None, None
    s = s.strip().lower()
    m = re.fullmatch(r'([a-z_]+)(\d+)', s)
    if not m:
        return None, None
    return m.group(1), int(m.group(2))

def rewrite_speed_from_scene_index(input_csv: str, output_csv: str):
    df = pd.read_csv(input_csv)
    df.columns = df.columns.str.strip()

    labels, values = [], []
    for sp in df["speed"]:
        scene, idx = parse_scene_index(sp)
        if scene in SCENE_INDEX_TO_LABEL and idx in SCENE_INDEX_TO_LABEL[scene]:
            label = SCENE_INDEX_TO_LABEL[scene][idx]
            value = LABEL_TO_VALUE[label]
        else:
            label, value = None, None  # unmatched → leave as None so it's easy to spot
        labels.append(label)
        values.append(value)

    # Keep label for debugging, overwrite speed with numeric
    df["speed_label"] = labels
    df["speed"] = values

    out_path = Path(output_csv)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_path, index=False)
    print(f"Saved: {out_path}")


def mbps_to_kbps(s: str):
    if not isinstance(s, str):
        return s
    s = s.strip().lower()
    m = re.match(r'^(\d+(?:\.\d+)?)\s*mbps$', s)
    if m:
        return int(float(m.group(1)) * 1000)
    m = re.match(r'^(\d+(?:\.\d+)?)\s*kbps$', s)
    if m:
        return int(float(m.group(1)))
    return s  # leave unchanged if it doesn't match

def rewrite_bitrate(input_csv: str, output_csv: str):
    df = pd.read_csv(input_csv)
    df.columns = df.columns.str.strip()
    df["bitrate"] = df["bitrate"].apply(mbps_to_kbps)

    out_path = Path(output_csv)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_path, index=False)
    print(f"Saved: {out_path}")

if __name__ == "__main__":
    project_root = Path(__file__).resolve().parent.parent
    input_dir = project_root / "csv/experiment1_adaptive_streaming_0908/res_only"

    for csv_file in input_dir.glob("*.csv"):
        # Save alongside original with "filtered_" prefix
        output_file = csv_file.parent.parent / "processed_res_only" / f"{csv_file.name}"
        rewrite_bitrate(csv_file, output_file)
        rewrite_speed_from_scene_index(output_file, output_file)

        # break