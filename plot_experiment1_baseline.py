import matplotlib.pyplot as plt
import os
import pandas as pd
import numpy as np
from scipy.stats import binom
from scipy.stats import binomtest
from datetime import datetime
from utils.utils import *
  

def get_y_range(nested_dict):
    """
    For each (bitrate, speed) cell:
    Computes the observed selection rate
    p = mean(scores) (i.e., fraction choosing “ours”).
    Computes a binomial predictive interval for the sample proportion:
    y_range[speed]: list of confidence ranges
    expected_prob[speed]: the point estimate p
    p_value[speed]: a one-sided binomial test vs 0.5 (H1: p > 0.5), Used later to put * or ** significance markers above bars.
    Run a binomial significance test to see if observers chose your method more than chance (p > 0.5).
    """
    y_range = {}
    expected_prob = {}
    p_value = {}
    for bitrate in bitrates:
        for speed in speeds:
            # initialize dictionary k v pair
            y_range[speed] = [] if speed not in y_range else y_range[speed]
            expected_prob[speed] = [] if speed not in expected_prob else expected_prob[speed]
            p_value[speed] = [] if speed not in p_value else p_value[speed]
            print(f'===== bitrate {bitrate}, speed {speed} =====')
            # compute binomial prob
            if bitrate in nested_dict and speed in nested_dict[bitrate]:
                # p = observed proportion of “successes”
                # Number of trials (N), i.e., how many observers/data points contributed to this condition.
                p = sum(nested_dict[bitrate][speed]) / len(nested_dict[bitrate][speed]) # selected percentage
                # N = len(nested_dict[bitrate][speed])
                # 2.5% of the binomial(N, p) distribution lies below k[0]
                # 97.5% lies below k[1]
                k = binom.ppf(cumulative_threshold, N, p) # inverse CDF of the binomial
                print(f'bitrate {bitrate}, N {N}')
                print(f'len(nested_dict[bitrate][speed]) {len(nested_dict[bitrate][speed])}\n')
                # This gives the central 95% range you’d expect for the observed share with sample size N if the true probability were p.
                # it gives the central 95% prediction interval for the number of successes if the true probability were p
                # Meaning: if the true preference rate p is 60%, then in 95% of repeated samples of 30 people, 
                # the observed rate will fall between 40% and 80%.
                binom_range = k/N
                mid = (binom_range[1] - binom_range[0]) / 2 + binom_range[0]
                print(f'p {p}, k {k/N}, mid {mid}')
                y_range[speed].append(tuple(binom_range))
                expected_prob[speed].append(p)
                # results of a binomial test, used later to put * or ** significance markers above bars.
                p_value[speed].append(binomtest(int(sum(nested_dict[bitrate][speed])), len(nested_dict[bitrate][speed]), 0.5, 'greater'))
    return y_range, expected_prob, p_value


if __name__ == "__main__":
    bitrates = [1000, 2000, 4000, 8000]
    speeds = [1, 1.5, 2] # ['v1', 'v2', 'v3'] [0.5, 1, 2] 
    separator_positions = [3, 6, 9, 12]  # Positions where separators are drawn

    # x_labels = [f"{speeds_dict[speed]}_{bitrates_dict[bitrate]}Mbps" for bitrate in bitrates for speed in speeds]
    x_labels = [f"{speeds_dict[speed]}" for bitrate in bitrates for speed in speeds]
    cumulative_threshold = [0.025, 0.975] # Cumulative probability threshold, 95% confidence interval
    # baseline 3 scenes, res only 6 scenes
    # number_of_observers = 10
    # N = number_of_observers * 3 * 3 # Number of trials: 10 participants 3 test scenes, 3 speeds, 4 bitrates, each scene has 3 paths?
    # folder_path = r'C:\Users\15142\new\Falcor\Source\Samples\EncodeDecode\experimentResult'
    exp_name = "experiment1_adaptive_streaming_0908"
    exp_type = "baseline" # "baseline"  "res_only"
    data_type = "mixed" # dynamic static mixed

    # Prepare the x positions for the plot
    x_positions = list(range(len(x_labels)))
    print(f'x_labels {x_labels}') # x_labels ['Slow', 'Medium', 'Fast',

    N = None
    if data_type == "static":
        folder_path = r'C:\Users\15142\new\Falcor\Source\Samples\EncodeDecode\experimentResult'
        N = 10 * 9 # 90 points in 1 bitrate, number oberservers * number of clips
    elif data_type == "dynamic":
        folder_path = f"csv/{exp_name}/processed_{exp_type}"
        N = 10 * 6 # 60 points in 1 bitrate, number oberservers * number of clips
    elif data_type == "mixed":
        folder_path = f"csv/{exp_name}/baseline_mixed"
        N = 10 * 9 + 10 * 6
    
    PROCESS_CSV = False # True False
    DEBUG = False
    if PROCESS_CSV:
        # x_positions = read_csv_value(folder_path)
        csv_val_dict = process_csv_value(folder_path)
        # y_ranges, expected_prob = get_y_range(csv_val_dict)


    # under 95%, the probability of people selecting our approach is within the range k/N
    # Plot vertical lines
    # X-axis: 12 positions = 4 bitrates × 3 speeds. Labels repeat Slow, Medium, Fast for each bitrate block, with dashed separators and text labels 1/2/4/8 Mbps.
    # Each point (the dot in the bar): the observed selection rate p at that (bitrate, speed), #ppl choose our method/total # data points for that (btirate, speed).
    # Error bar: the 95% binomial predictive range for the sample proportion given N and p (not a CI for the true p).
    # Horizontal dashed line at 0.5 marks “coin-flip” baseline.
    # Significance stars: * if p > 0.5 at p<0.05, ** if p<0.01 (one-sided binomial test).
    # The figure note N = 10 × 3 × 3 explains the trial count used in the binomial math.
    PLOT = True # True False
    SAVE = True
    SHOW = False
    if PLOT:
        csv_val_dict = process_csv_value(folder_path)
        y_ranges, expected_prob, p_value = get_y_range(csv_val_dict)
        # print(f'y_ranges \n {y_ranges}')
        # print(f'expected_prob \n {expected_prob}')

        plt.figure(figsize=(10, 6))
        for i, (bitrate, speed) in enumerate([(b, s) for b in bitrates for s in speeds]):
            y_min, y_max = y_ranges[speed][bitrates.index(bitrate)]
            prob = expected_prob[speed][bitrates.index(bitrate)]
            y_error = np.array([y_max - prob, prob - y_min]).reshape(2, -1)
            # print(f'y_error {y_error}')
            plt.errorbar(i, prob, yerr=y_error, color=colors[speed], ecolor=colors[speed], \
                        elinewidth=5, capsize=8, label=speed if i % len(speeds) == 0 else "")
            plt.scatter(i, prob, color=colors[speed], marker='o', s=100, label=f'prob{prob}', )  # '^' is the triangle marker pointing upwards
            plt.text(i - 0.4, y_min - 0.08, f'{round(prob, 2)}', color='black', fontsize=18, ha='left', va='bottom')  # Adjust position with `ha` and `va`
            # significance value
            print(f'\np_value {p_value[speed][bitrates.index(bitrate)].pvalue}')
            if p_value[speed][bitrates.index(bitrate)].pvalue < 0.01:
                print(f'p_value < 0.01')
                plt.text(i -0.18, y_min - 0.04, '**', color='black', fontsize=18, ha='left', va='bottom') 
            elif p_value[speed][bitrates.index(bitrate)].pvalue < 0.05:
                print(f'p_value < 0.05')
                plt.text(i -0.1, y_min - 0.04, '*', color='black', fontsize=18, ha='left', va='bottom')  # Adjust position with `ha` and `va`

        plt.axhline(0.5, color='lightgrey', linestyle='--', linewidth=2, label="y = 0.5")
        plt.text(10.8, 0.42, "p = 0.5", color='darkgrey', fontsize=18, ha='center')

        # Draw vertical lines to separate bitrates and label them
        for idx, pos in enumerate(separator_positions):
            if pos != 12:
                plt.axvline(x=pos - 0.5, color='gray', linestyle='--', linewidth=1)
            # Add bitrate label beside the line
            if idx < len(bitrates):  # Ensure labels match the number of groups
                plt.text(pos - 0.5, 0, f'{bitrates_array[idx]}', fontsize=18, color='gray', ha='right', va='bottom')

        # Add x-axis labels and adjust layout
        plt.xticks(x_positions, x_labels, rotation=45, ha="right", fontsize=15)
        plt.xlim(-0.5, 11.5)
        plt.yticks(fontsize=15)
        plt.ylim(0, 1.05)
        # plt.ylabel(f"Probability of selecting ours", fontsize=15)

        if data_type == "static":
            plt.ylabel(f"Static scenes - probability of selecting ours", fontsize=15)
        elif data_type == "dynamic":
            plt.ylabel(f"Dynamic scenes - probability of selecting ours", fontsize=15)
        elif data_type == "mixed":
            plt.ylabel(f"Probability of selecting ours", fontsize=15)
  
        plt.tight_layout()

        # plt.text(
        #     0.1, 0.91,  # Coordinates in figure-relative units
        #     f"N = {number_of_observers} x 3 x 3",  # Text to display
        #     fontsize=15,
        #     color="black",
        #     transform=plt.gcf().transFigure,  # Transform coordinates to figure-relative
        #     ha="left", va="bottom"  # Align text to bottom-left
        # )

        now = datetime.now()
        plot_pth = now.strftime("%Y-%m-%d-%H_%M")
        if SAVE:
            output_dir = f"outputs/{exp_name}"
            # if data_type == "static":
            filename = f"{output_dir}/experiment1-{exp_type}-{data_type}-{plot_pth}.png" 
            # elif data_type == "dyna" else \
            # f"{output_dir}/experiment1-{exp_type}-dynamic-{plot_pth}.png"
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            plt.savefig(filename, dpi=300, bbox_inches='tight')
            print(f'Successfully saved to {output_dir}/experiment1-{exp_type}-{plot_pth}.png')
        if SHOW:
            print('show')
            plt.show()
