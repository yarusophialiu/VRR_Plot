plot heatmap - VRRML

experiment1: adaptive streaming


folder_path = "csv/experiment1_adaptive_streaming"


plot_experiment1.py
Plot for adaptive streaming experiment.

plot_experiment2.py


res only baseline:
static scenes: "sibenik" "breakfastroom" "salledebain", speed 1, 1.5, 2


scene index speed map
breakfastroom 3 → Slow
salledebain 3 → Slow
breakfastroom 1 → Slow
breakfastroom 2 → Slow
school 2 → Slow

salledebain 1 → Medium
salledebain 2 → Medium
school 1 → Medium
rogue 2 → Medium
makeway 1 → Medium

sibenik 3 → Fast
sibenik 1 → Fast
rogue 1 → Fast
makeway 2 → Fast
sibenik 2 → Fast

SCENE_INDEX_TO_LABEL = {
    "breakfastroom": {1: "Slow",   2: "Slow",   3: "Slow"},
    "salledebain":   {1: "Medium", 2: "Medium", 3: "Slow"},
    "sibenik":       {1: "Fast",   2: "Fast",   3: "Fast"},
    
    "school":        {1: "Medium", 2: "Slow"},
    "rogue":         {1: "Fast",   2: "Medium"},
    "makeway":       {1: "Medium", 2: "Fast"},
}
