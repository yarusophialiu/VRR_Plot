import os
import random
import numpy as np
import pandas as pd
from datetime import datetime, date
from utils.utils import *
import matplotlib.pyplot as plt
import importlib.util
import shutil
import ast
import os



def type2(df, label_idx, bitrate, number, max_jod, max_res):
    """x axis is resolution, y axis is JOD, color is bitrate, labels are refresh rate"""
    bitrate_df = df.iloc[label_idx, 0] # check if bitrate is correct
    if DEBUG:
        print(f'bitrate_df {bitrate_df}, bitrate {bitrate}')

    for num in range(number): # loop column
        jod_cvvdp = df.iloc[label_idx, 1+5*num:6+5*num].values
        # print(f'jod_cvvdp {jod_cvvdp}')
        jod_cvvdp = [float(v) for v in jod_cvvdp]   

        max_jod_idx = np.argmax(jod_cvvdp)
        # print(f'idx {num}, fps{refresh_rate[num]}, JOD {jod_cvvdp}, max JOD {max(jod_cvvdp)}')
        max_jod.append(max(jod_cvvdp))
        max_res.append(x_values[max_jod_idx])


def find_comb_within_range(df, label_idx, JODDROP, max_comb_per_sheet):
    """
    res, fps whose jod is within range of the biggest of the sheet
    max_comb_per_sheet for path1_seg2_3 is like [[80, 480, 7.1158], [120, 720, 7.5596], [120, 720, 7.7879], [120, 720, 7.9228]]
    """
    comb_within_range_per_sheet = []

    for num in range(len(refresh_rate)): # loop column
        jod_cvvdp = df.iloc[label_idx, 1+5*num:6+5*num].values
        jod_cvvdp = [float(v) for v in jod_cvvdp] 
        # Find values within THRESHOLD 0.25 range of the maximum
        max_jod_val_per_bitrate = max_comb_per_sheet[label_idx][2]
        close_to_max = [(index, value) for index, value in enumerate(jod_cvvdp) if abs(max_jod_val_per_bitrate - value) <= JODDROP]
        # print(f"\nBitrate {bitrate}, Maximum JOD: {max_jod_val_per_bitrate}")
        if len(close_to_max) == 0:
            continue  
        # print("Values within 0.25 range of the maximum:", close_to_max)   
        for index, jod in close_to_max:
            # print(f'jod, refresh_rate, resolution {jod, refresh_rate[num], x_values[index]}')
            comb_within_range_per_sheet.append((refresh_rate[num], x_values[index]))
    return comb_within_range_per_sheet


def dropJOD(all_scenes, filename, drop_range):
    # Load the file as a module
    spec = importlib.util.spec_from_file_location("data_module", filename)
    data_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(data_module)

    for scene in all_scenes:
        variable_name = f"{scene}_within_JOD_range"
        print(f'variable_name {variable_name}')
        if not hasattr(data_module, variable_name):  # Check if variable exists in the module
            print(f'{variable_name} not exits, continue...')
            continue
        comb_within_range = getattr(data_module, variable_name)
        print(f'comb_within_range {variable_name} {drop_range}\n')
        # print(f'comb_within_range {comb_within_range}\n\n\n')
        min_data = {}
        for key, value in comb_within_range.items():
            min_data[key] = []  
            count = 0
            for sublist in value: # # value represents 4 bitrates, sublist represents 1 bitrate
                # print(f'=================== count {count} ===================')
                # Find the minimum fps * resolution product
                min_product = min(t[0] * t[1] * t[1] for t in sublist) # f * h^2
                # Get all tuples with the minimum product
                min_tuples = [t for t in sublist if t[0] * t[1] * t[1] == min_product]
                selected_tuple = random.choice(min_tuples)

                min_data[key].append([selected_tuple[0], selected_tuple[1]])
                count += 1
        # print(f'min_data {min_data}\n\n\n')

        new_filename = f"{output_dir}/cleaned_{filename}"
        with open(new_filename, "a") as f:
            f.write(f"{variable_name}_{int(drop_range * 100)} = {min_data}")
            f.write(f"\n")
        print(f'Successfully write to {new_filename}.')




def skip_paths(scene, path_name):
    if scene in exclude_paths:
        if path_name in exclude_paths[scene]:
            return True
    return False


def find_max_saving_per_path(optimal_fps, optimal_res, comb_per_sheet, DEBUG=False):
    optimal_cost  = optimal_fps * (optimal_res ** 2)
    # Compute savings
    max_saving = float('-inf')
    best_pair = None
    if DEBUG:
        print(f'optimal_cost  {optimal_cost }')

    for fps, res in comb_per_sheet:
        candidate_cost  = fps * (res ** 2)
        if DEBUG:
            print(f'candidate_cost {candidate_cost}')
        saving = optimal_cost  - candidate_cost
        if saving > max_saving:
            max_saving = saving
            best_pair = (fps, res)
    if DEBUG:
        print(f'best_pair {best_pair}, max_saving {max_saving}')
    return max_saving, optimal_cost


def compute_saving(excel_date, bitrates, JODDROP, WRITE=False):
    total_saving = {}
    for scene_name in SCENES:
        print(f'\n================================== SCENE {scene_name} JODDROP {JODDROP} ==================================')
        file_path = f'excel/data-{excel_date}/{scene_name}.xlsx'
        # print(f'file_path {file_path}')
        max_comb_per_sequence = {} # per scene
        comb_within_range_per_sequence = {} 
        saving_per_bitrate = {}
        for bitrate in bitrates:
            print(f'=============================== bitrate {bitrate} ===============================')
            max_comb_per_bitrate = {} # { path1_seg1: [[fps1, res1], [fps2, res2], [fps3, res3]] }
            dropjod_saving = []
            dropjod_saving_dict = {}
            MAX_SAVING_0 = False
            for path in range(1, 6):
                for seg in range(1, 4):
                    sequence_name = f'path{path}_seg{seg}'
                    max_comb_per_bitrate[sequence_name] = []
                    # print(f'max_comb_per_bitrate {jod_cvvdp = [float(v) for v in jod_cvvdp]}')
                    for speed in range(1, 4):
                        sheet_name = f'path{path}_seg{seg}_{speed}'
                        # print(f'sheet_name {sheet_name}')
                        if skip_paths(scene_name, sheet_name):
                            print(f'Skip {scene_name}, {sheet_name} {bitrate}mbps')
                            continue
                        # print(f'sheet_name {sheet_name}')
                        max_comb_per_sequence.setdefault(sheet_name, [])
                        comb_within_range_per_sequence.setdefault(sheet_name, [])

                        excel_file = pd.ExcelFile(file_path)
                        if sheet_name in excel_file.sheet_names:
                            df = pd.read_excel(excel_file, sheet_name=sheet_name, na_values=['NA'])
                        else:
                            print(f'Sheet_name not exists, continue.')
                            continue
                        # df = pd.read_excel(file_path, sheet_name=sheet_name, na_values=['NA'])
                        # print(f'================== sheet_name {sheet_name} =================')
                        max_jod, max_res = [], [] # max_jod in all refresh rates
                        type2(df, bitrate_dict[bitrate], bitrate, len(refresh_rate), max_jod, max_res)
                        max_idx = np.argmax(max_jod) # only availble if type2 is run
                        # max_jod_val = max_jod[max_idx]
                        # print(f'\nmax_jod {max_jod} \nmax_res {max_res}')
                        optimal_fps, optimal_res = refresh_rate[max_idx], max_res[max_idx]
                        # print(f'bitrate {bitrate}, max JOD is {max_jod[max_idx]} with resolution {max_res[max_idx]} fps {refresh_rate[max_idx]}')
                        # print(f'\noptimal_fps, optimal_res {optimal_fps, optimal_res}')
                        # output is like: max_comb_per_sequence {'path1_seg2_3': [[80, 480, 7.1158], [120, 720, 7.5596], [120, 720, 7.7879], [120, 720, 7.9228]]}
                        max_comb_per_sequence[sheet_name].append([optimal_fps, optimal_res, max_jod[max_idx]])
                        comb_per_sheet = find_comb_within_range(df, bitrate_dict[bitrate], JODDROP, max_comb_per_sequence[sheet_name])
                        comb_within_range_per_sequence[sheet_name].append(comb_per_sheet)
                        # print(f'max_comb_per_sequence[sheet_name] {max_comb_per_sequence[sheet_name]}')
                        # print(f'max_comb_per_bitrate {max_comb_per_bitrate}')
                        # print(f'comb_per_sheet {comb_per_sheet}')
                        max_saving, maxjod_cost = find_max_saving_per_path(optimal_fps, optimal_res, comb_per_sheet)
                        dropjod_saving.append((maxjod_cost, max_saving))
                        dropjod_saving_dict[sheet_name] = (maxjod_cost, max_saving)
                        # if max_saving == 0:
                        #     print(f'\noptimal_fps, optimal_res, comb_per_sheet\n{optimal_fps, optimal_res, comb_per_sheet}')
                        #     find_max_saving_per_path(optimal_fps, optimal_res, comb_per_sheet, DEBUG=True)
                        #     # MAX_SAVING_0 = True
                        #     break
                        # min_data[key].append([selected_tuple[0], selected_tuple[1]])
                    if MAX_SAVING_0:
                        break
            # print(f'{bitrate}kbps {max_comb_per_bitrate}')
                if MAX_SAVING_0:
                    break
                # break
            # dropjod_saving = np.array(dropjod_saving, dtype=np.int64)
            # print(f'dropjod_saving length {len(dropjod_saving)}, sum {dropjod_saving.sum()}')
            # saving_per_path = dropjod_saving.sum() / len(dropjod_saving)
            saving_per_bitrate[bitrate] = dropjod_saving
            # print(f'saving_per_path {len(dropjod_saving)}')
            # break
        # print(f'max_comb_per_sequence {max_comb_per_sequence}')
        # print(f'comb_within_range_per_sequence \n{comb_within_range_per_sequence}')
        # print(f'saving_per_bitrate {saving_per_bitrate}')
        total_saving[scene_name] = saving_per_bitrate
    # print(f'total_saving {total_saving}')
    
    if WRITE:
        with open(total_saving_file, "a") as file:
            file.write("\n") 
            file.write(f"{total_saving}")
    return total_saving


def get_average_saving_per_bitrate(total_saving_dict, path='', WRITE=False): 
    """
    total_saving_dict is like {
        'bedroom': {
            1000: [(34992000, 0), (69984000, 44064000), ... 45 paths (maxjod cost, dropjod saving)]
            2000: ...
        }, 'bistro': {
            1000: [(34992000, 0), (69984000, 44064000), ... 45 paths (maxjod cost, dropjod saving)]
            2000: ...
        }
    }
    """
    bitrate_saving = {}

    for scene, bitrate_data in total_saving_dict.items():
        print(f'scene {scene}')
        for bitrate, entries in bitrate_data.items(): # entries: [(34992000, 0), (69984000, 44064000)...]
            total_baseline = np.int64(0) # baseline(maxjod) and drop jod saving
            total_saving = np.int64(0)
            for baseline, saving in entries: # (34992000, 0) (maxjod cost, dropjod saving)
                total_baseline += baseline
                total_saving += saving
            saving_percentage = 100 * total_saving / total_baseline if total_baseline > 0 else 0
            if bitrate not in bitrate_saving:
                bitrate_saving[bitrate] = []
            bitrate_saving[bitrate].append(saving_percentage)
        print(f'bitrate_saving {bitrate_saving}')

    # Average percentage saving per bitrate across all scenes
    average_saving_per_bitrate = {bitrate: round(sum(savings)/len(savings), 3) for bitrate, savings in bitrate_saving.items()}
    if WRITE:
        with open(path, "a") as file:
            file.write("\n") 
            file.write(f"dropjod_{int(JODDROP*100)} = {average_saving_per_bitrate}")
    return average_saving_per_bitrate



# paper Fig 11: Average percentage reduction in pixels rendered per second
# given jod, find the saving of f * r^2
if __name__ == "__main__":
    SAVE = False # True, False
    SHOW = False
    DEBUG = False
    # WRITE_LABELS_WITHIN_JOD_RANGE = True # True False write all labels within JOD range to python file
    # JODDROP = 0.25 # TODO: change threshold
    COMPUTE = False
    COMPUTE_SAVING = True # True, False
    WRITE_TOTAL_SAVING_DICT = False
    WRITE_SAVING_PERCENT = True
    PLOT = True
    bitrates = [1000, 1500, 2000, 3000, 4000]
    # bitrates = [1000, 1500]
    JODS = [0.1 * i for i in range(1, 21)]
    # JODS = [0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1. , 1.1, 1.2, 1.3,
    #    1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 2.]
    
    # bitrate_dict = {bitrate: index for index, bitrate in enumerate(bitrates)}
    bitrate_dict = {1000: 0, 1500: 1, 2000: 2, 3000: 3, 4000: 4}
    print(f'bitrate_dict {bitrate_dict}')
    x_values = [360, 480, 720, 864, 1080] # resolution
    print(f'x_values {x_values}')
    
    SCENES = ['bedroom', 'bistro', 'crytek_sponza', 'gallery', 'living_room', 'lost_empire', 'room', 'sibenik', 'suntemple', 'suntemplestatue']
    # SCENES = ['bedroom', 'bistro']
    excel_date = '1-to-4mbps' # '400_700_900kbps' 1-to-4mbps
    # drop_jod_file = 'drop_jod_range25-0425-2206.py'
    # JODDROP = 0


    # today = get_today()
    today = '2025-05-24'
    output_dir = f'pyoutput/{today}'
    os.makedirs(output_dir, exist_ok=True)
    now = datetime.now()
    time_path = now.strftime("%m%d-%H%M")
    
    if COMPUTE:
        for JODDROP in JODS:
            print(f'================= JODDROP {JODDROP} =================')
            total_saving_file = f"{output_dir}/total_saving_dropJOD{int(JODDROP*100)}-{time_path}.py"
            print(f'total_saving_file: {total_saving_file}')
            if COMPUTE_SAVING:
                total_saving_dict = compute_saving(excel_date, bitrates, JODDROP, WRITE=WRITE_TOTAL_SAVING_DICT) 
            
            # if not WRITE_TOTAL_SAVING_DICT:
            #     file_path = f'{output_dir}/total_saving_dropJOD25-0523-2103.py'
            #     with open(file_path, "r") as file:
            #         content = file.read()
            #         total_saving_dict = ast.literal_eval(content)

            saving_percent_path = f"{output_dir}/saving_percent_JOD.py"
            if WRITE_SAVING_PERCENT:
                average_saving_per_bitrate = get_average_saving_per_bitrate(total_saving_dict, saving_percent_path, WRITE=WRITE_SAVING_PERCENT)
                print(f'average_saving_per_bitrate {average_saving_per_bitrate}')
            

    savings_by_bitrate = {br: [] for br in bitrates}
    if PLOT:
        colors = ['deepskyblue', 'gold', 'salmon', 'palegreen', 'plum',] # dodgerblue darkorange
        plt.figure(figsize=(10,6)) # width=10 inches, height=6 inches

        for joddrop in JODS:
            module_name = f"saving_percent_JOD"
            file_path = os.path.join(output_dir, f"{module_name}.py")
            
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            data = getattr(module, f"dropjod_{int(joddrop * 100)}")

            # Store saving values for each bandwidth
            for br in bitrates:
                savings_by_bitrate[br].append(data[br])
        # print(f'savings_by_bitrate {savings_by_bitrate}')
        for i, br in enumerate(bitrates):
            bitrate = int(br/1000) if br != 1500 else (br/1000)
            plt.plot([j for j in JODS], savings_by_bitrate[br], marker='o', color=colors[i], label=f"{bitrate} Mbps")
        
        plt.xticks(JODS)
        plt.xlabel("Quality reduction (JOD)", fontsize=15)
        plt.ylabel(f"Average % rendering saving", fontsize=15)
        plt.grid(True, color='lightgrey', linestyle='--')
        plt.legend(title="Bitrate", fontsize=15)
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(f'imageoutput/dropjod_saving.svg')
        plt.show()

        # read 

