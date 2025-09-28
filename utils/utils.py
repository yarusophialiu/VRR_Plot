import os
import pandas as pd
from datetime import date


VRR_HPC = r'C:\Users\15142\Projects\VRR\VRR_Remote_Server\VRR_HPC'

speeds_dict = {1: 'Slow', 1.5: 'Medium', 2: 'Fast'}
bitrates_dict = {1000: 1, 2000: 2, 4000: 4, 8000: 8}
bitrates_array = ['1Mbps ', '2Mbps ', '4Mbps ', '8Mbps ']

colors = {
    1: "gold", # 0.5
    1.5: "deepskyblue", # 1
    2: "salmon" # 2
}


refresh_rate = [30, 40, 50, 60, 70, 80, 90, 100, 110, 120]
resolution_to_idx = {360: 0, 480: 1, 720: 2, 864: 3, 1080: 4}
SCENES = ['bedroom', 'bistro', 'crytek_sponza', 'gallery', 'living_room', 'lost_empire', \
          'room', 'sibenik', 'suntemple', 'suntemplestatue']


# this is used to skip paths without cvvdp results and invlid motion
exclude_paths = {
    # 'bistro': ['path5_seg3_1', 'path5_seg3_2', 'path5_seg3_3'],
    'room': ['path5_seg2_2', 'path5_seg2_3', 'path1_seg1_2', 'path3_seg3_3', 'path3_seg1_3', 'path4_seg1_3', 'path4_seg2_1', 'path5_seg3_1', 'path5_seg3_2', 'path5_seg3_3'],
    # 'sibenik': ['path3_seg2_2', 'path3_seg3_2', 'path5_seg3_3'],
    # 'living_room': ['path1_seg1_2', 'path3_seg3_3', 'path5_seg3_1'],
    'living_room': ['path5_seg3_1'],
    'lost_empire': ['path3_seg3_1'],
    'suntemplestatue': ['path4_seg3_1'],
    'suntemple': ['path1_seg3_1', 'path2_seg1_1', 'path2_seg1_3', 'path2_seg3_1', 'path3_seg1_3', 'path4_seg3_1'],
    # 'crytek_sponza': ['path1_seg1_1'],
    # 'gallery': ['path5_seg3_3']
}


def get_today():
    return date.today()



# def read_csv_value(folder_path, DEBUG=False):
#     """
#     collect bitrate, speed, choice from every csv
#     result_list is like [[1000.0, 1.0, 1.0], [8000.0, 2.0, 1.0], ...] 
#     """
#     result_list = []
#     for file_name in os.listdir(folder_path):
#         # print(f'file_name {file_name}')
#         if file_name.endswith('.csv'):
#             file_path = os.path.join(folder_path, file_name)
#             # data = pd.read_csv(file_path)
#             data = None
#             if os.path.getsize(file_path) > 0:  # non-empty file
#                 data = pd.read_csv(file_path)
#             else:
#                 continue
#             # print()
#             result_list.extend(data.iloc[:, [2, 3, 4]].values.tolist()) # v3 [2,3,5] bitrate, speed, score
#     if DEBUG:
#         print(f'x_positions {result_list}\n\n\n')
#     return result_list

def read_csv_value(folder_path, scenes_to_keep=None, DEBUG=False):
    """
    collect bitrate, speed, choice from every csv
    result_list is like [[1000.0, 1.0, 1.0], [8000.0, 2.0, 1.0], ...] 
    Only rows from scenes_to_keep are included if provided.
    """
    result_list = []
    for file_name in os.listdir(folder_path):
        if file_name.endswith('.csv'):
            file_path = os.path.join(folder_path, file_name)
            if os.path.getsize(file_path) == 0:
                continue

            data = pd.read_csv(file_path)

            # filter by scene if requested
            if scenes_to_keep is not None and "scene" in data.columns:
                data = data[data["scene"].isin(scenes_to_keep)]

            # collect only [bitrate, speed, score]
            result_list.extend(data.iloc[:, [2, 3, 4]].values.tolist())

    if DEBUG:
        print(f"x_positions {result_list}\n\n\n")
    return result_list


def process_csv_value(folder_path, scenes_to_keep=None, DEBUG=False):
    """
    Groups scores into a nested dict by bitrate then speed:
    nested[bitrate][speed] -> [score, score, ...].
    nested_dict: {1000.0: {1.0: [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0], 2.0: [1.0, 1.0, ...], ...}
    """
    x_positions = read_csv_value(folder_path, scenes_to_keep=scenes_to_keep, DEBUG=DEBUG)
    nested_dict = {}
    for bitrate, speed, score in x_positions:
        if bitrate not in nested_dict:
            nested_dict[bitrate] = {}  # Initialize sub-dictionary for this bitrate
        if speed not in nested_dict[bitrate]:
            nested_dict[bitrate][speed] = []  # Initialize an empty list for this speed
        nested_dict[bitrate][speed].append(score)  # Append the score to the list for this speed
    if DEBUG:
        # Debug: print the counts
        for bitrate in nested_dict:
            for speed in nested_dict[bitrate]:
                print(f"bitrate={bitrate}, speed={speed}, count={len(nested_dict[bitrate][speed])}")
    if DEBUG:
        print(f'nested_dict {nested_dict}')
    return nested_dict