from pathlib import Path
import pandas as pd


def remove_scenes(input_csv: str, output_csv: str, scenes_to_remove=None):
    """
    Remove rows from a CSV where the 'scene' column matches given values.
    Args:
        scenes_to_remove (list[str], optional): Scenes to drop. 
            Defaults to ["sibenik", "salledebain", "breakfastroom"].
    """
    if scenes_to_remove is None:
        scenes_to_remove = ["sibenik", "salledebain", "breakfastroom"]

    df = pd.read_csv(input_csv)
    df.columns = df.columns.str.strip()

    # Filter
    df_filtered = df[~df["scene"].isin(scenes_to_remove)]

    print(df_filtered)

    # Save
    df_filtered.to_csv(output_csv, index=False)
    print(f"Filtered CSV saved to: {output_csv} "
          f"(removed {len(df) - len(df_filtered)} rows)")


# exclude csv rows, that contain unwanted scene
if __name__ == "__main__":
    # Example usage
    # input_csv = "../csv/experiment1_adaptive_streaming_0908/baseline/experiment_baseline_20250904_194528.csv"
    # output_csv = "../csv/experiment1_adaptive_streaming_0908/baseline/filtered_experiment_baseline_20250904_194528.csv"
        # Base project root (two levels up from utils/)
    project_root = Path(__file__).resolve().parent.parent

    input_csv = project_root / "csv/experiment1_adaptive_streaming_0908/baseline/experiment_baseline_20250904_194528.csv"
    output_csv = project_root / "csv/experiment1_adaptive_streaming_0908/baseline/filtered_experiment_baseline_20250904_194528.csv"

    remove_scenes(input_csv, output_csv)
