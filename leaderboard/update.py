import json
import os
import re
import math
from pathlib import Path
from collections import defaultdict
from statistics import mean, stdev
import argparse

def get_all_models_from_results(results_dir):
    """Get all unique model names from JSON file names in results directory."""
    models = {}

    for subdir in ['cloud', 'local']:
        results_subdir = Path(results_dir) / subdir
        if results_subdir.exists():
            for file_path in results_subdir.glob('*.json'):

                file_name = file_path.stem  
                if file_name.startswith('result_'):
                    model_name = file_name[len('result_'):]  
                    if model_name:  

                        base_model = model_name
                        if base_model.endswith(('_2', '_3', '_4', '_5')):
                            base_model = base_model[:-2]  

                        if base_model not in models:
                            models[base_model] = subdir  
                        else:

                            pass

    return models

def load_color_mapping(color_mapping_path):
    """Load the color mapping JSON file."""
    with open(color_mapping_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_color_mapping(color_mapping_path, color_mapping):
    """Save the color mapping JSON file."""
    with open(color_mapping_path, 'w', encoding='utf-8') as f:
        json.dump(color_mapping, f, indent=2, ensure_ascii=False)

def check_models():
    """Check models functionality - find unassigned and unused models."""

    results_dir = Path('../results')
    color_mapping_path = Path('./color_mapping.json')

    all_models_with_source = get_all_models_from_results(results_dir)
    all_models = set(all_models_with_source.keys())

    color_mapping = load_color_mapping(color_mapping_path)

    assigned_models = set()
    for category, models in color_mapping.items():
        assigned_models.update(models)

    unassigned_models = all_models - assigned_models
    if unassigned_models:
        print(f"\nFound {len(unassigned_models)} unassigned models:")
        for model in sorted(unassigned_models):
            print(f"  - {model}")
    else:
        print("\nNo unassigned models found.")

    unused_models = assigned_models - all_models
    if unused_models:
        print(f"\nFound {len(unused_models)} unused models in color mapping:")
        for model in sorted(unused_models):

            for category, models in color_mapping.items():
                if model in models:
                    print(f"  - {model} (in {category})")
    else:
        print("\nNo unused models found in color mapping.")

    print(f"\nTo update the color mapping interactively, run: python update.py --interactive\nRunning 'python update.py' in an interactive terminal will also start interactive mode.")

def interactive_main():
    """Interactive version of the main function that allows users to make changes directly"""

    results_dir = Path('../results')
    color_mapping_path = Path('./color_mapping.json')

    all_models_with_source = get_all_models_from_results(results_dir)
    all_base_models = set(all_models_with_source.keys())

    all_actual_models = set()
    for base_model in all_base_models:

        all_actual_models.add(base_model)

        for suffix in ['_2', '_3', '_4', '_5']:
            all_actual_models.add(base_model + suffix)

    color_mapping = load_color_mapping(color_mapping_path)

    assigned_models = set()
    for category, models in color_mapping.items():
        assigned_models.update(models)

    unassigned_models = all_base_models - assigned_models
    if unassigned_models:
        for model in sorted(unassigned_models):
            folder = all_models_with_source[model]  

            print(f"\n{model} has not been assigned. Where should I assign it?")

            if folder == 'cloud':
                print("1. cloud_closed")
                print("2. cloud_open")
                valid_choices = {'1': 'cloud_closed', '2': 'cloud_open'}
            else:  
                print("1. local_instruct")
                print("2. local_thinking")
                valid_choices = {'1': 'local_instruct', '2': 'local_thinking'}

            while True:
                try:
                    choice = input("Enter choice (1/2): ").strip()

                    if choice in valid_choices:
                        category = valid_choices[choice]
                        color_mapping[category].append(model)
                        print(f"Assigned to {category}")
                        break
                    else:
                        print("Invalid choice. Please enter 1 or 2.")
                except (ValueError, IndexError):
                    print("Invalid input. Please enter 1 or 2.")

    unused_models = assigned_models - all_actual_models
    if unused_models:
        for model in sorted(unused_models):

            for category, models in color_mapping.items():
                if model in models:
                    color_mapping[category].remove(model)
                    print(f"\n{model} was assigned to {category} but has no result file. It was Removed from the color_mapping.")
                    break

    for category in color_mapping:
        color_mapping[category] = sorted(color_mapping[category])

    save_color_mapping(color_mapping_path, color_mapping)
    print(f"Updated color_mapping.json saved.")

def get_model_name_from_filename(filename):
    name = filename.replace('result_', '').replace('.json', '')
    base_name = re.sub(r'_(2|3|4|5|6|7|8|9|10|11|12|13|14|15|16|17|18|19|20)$', '', name)
    return base_name

def convert_amount_to_numeric(amount_str):
    numeric_str = amount_str.replace('€', '')
    numeric_str = numeric_str.replace('.', '')
    try:
        return float(numeric_str)
    except ValueError:
        return 0.0

def map_correct_answers_to_prize(correct_answers):
    prize_values = [
        "0€", "50€", "100€", "200€", "300€", "500€", 
        "1.000€", "2.000€", "4.000€", "8.000€", "16.000€", 
        "32.000€", "64.000€", "125.000€", "500.000€", "1.000.000€"
    ]
    index = min(int(correct_answers), 15) if correct_answers >= 0 else 0
    return prize_values[index]

def convert_prize_to_numeric(prize_str):
    numeric_str = prize_str.replace('€', '')
    numeric_str = numeric_str.replace('.', '')
    try:
        return int(numeric_str)
    except ValueError:
        return 0

def calculate_log_percentage(value):
    a = 50.00500050005
    max_value = 1_000_000
    log_value = (math.log(value + a) - math.log(a)) / (math.log(max_value + a) - math.log(a)) * 100
    return max(0, min(100, log_value))  

def process_results_directory(results_dir):
    model_files = defaultdict(list)
    for filename in os.listdir(results_dir):
        if filename.endswith('.json') and filename.startswith('result_') and not os.path.isdir(os.path.join(results_dir, filename)):
            filepath = os.path.join(results_dir, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                try:
                    data = json.load(f)
                    model_name = get_model_name_from_filename(filename)
                    model_files[model_name].append((filepath, filename))
                except json.JSONDecodeError:
                    print(f"Error decoding JSON in file: {filename}")
                    continue

    leaderboard_data = []
    all_average_scores = []  
    for model_name, files in model_files.items():
        if not files:
            continue
        average_scores = []
        for filepath, filename in files:
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                rounds = data.get('rounds', [])
                correct_answers_list = [round_data.get('correct_answers', 0) for round_data in rounds]
                sorted_answers = sorted(correct_answers_list)
                n = len(sorted_answers)
                if n > 10:  
                    middle_35_answers = sorted_answers[5 : n - 5]  
                else:
                    middle_35_answers = sorted_answers
                if middle_35_answers:
                    prize_values = [map_correct_answers_to_prize(ca) for ca in middle_35_answers]
                    numeric_values = [convert_prize_to_numeric(prize) for prize in prize_values]
                    average_score = mean(numeric_values)
                else:
                    average_score = 0  
                average_scores.append(average_score)
                all_average_scores.append(average_score)  
            except json.JSONDecodeError:
                print(f"Error decoding JSON in file: {filename}")
                continue
            except Exception as e:
                print(f"Error processing file {filename}: {e}")
                continue
        if average_scores:
            sorted_averages = sorted(average_scores)
            n_averages = len(sorted_averages)
            if n_averages > 0:
                middle_idx = n_averages // 2
                bar_value = sorted_averages[middle_idx]
                min_average = min(sorted_averages)
                max_average = max(sorted_averages)
                low_deviation_euros = round(bar_value - min_average)
                high_deviation_euros = round(max_average - bar_value)
                if n_averages == 1:
                    low_deviation_euros = None
                    high_deviation_euros = None
            else:
                bar_value = 0
        else:
            bar_value = 0
        original_average = 0
        if files:
            try:
                filepath, filename = files[0]
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                avg_final_amount = data.get('average_final_amount', '0€')
                original_average = convert_amount_to_numeric(avg_final_amount)
            except:
                pass
        model_info = {
            'model_name': model_name,
            'median_value': round(bar_value),  
            'low_deviation_euros': low_deviation_euros,  
            'high_deviation_euros': high_deviation_euros,  
            'original_average': original_average,
            'log_percentage': float(f"{calculate_log_percentage(round(bar_value)):.1f}")  
        }
        leaderboard_data.append(model_info)

    global_max_value = max(all_average_scores) if all_average_scores else 1_000_000  
    sorted_leaderboard = sorted(leaderboard_data, key=lambda x: x['median_value'], reverse=True)
    for i, model_info in enumerate(sorted_leaderboard):
        model_info['rank'] = i + 1
    return {
        'models': sorted_leaderboard,
        'global_max_value': global_max_value
    }

def generate_leaderboard():
    """Generate leaderboard functionality."""

    local_data = process_results_directory('../results/local')
    with open('leaderboard_local.json', 'w', encoding='utf-8') as f:
        json.dump(local_data, f, indent=2, ensure_ascii=False)

    cloud_data = process_results_directory('../results/cloud')
    with open('leaderboard_cloud.json', 'w', encoding='utf-8') as f:
        json.dump(cloud_data, f, indent=2, ensure_ascii=False)

    print(f"Leaderboards generated: {len(local_data['models'])} local, {len(cloud_data['models'])} cloud models")

def main():
    parser = argparse.ArgumentParser(description='Update leaderboard and model assignments.')
    parser.add_argument('--interactive', '-i', action='store_true', help='Run interactive model assignment')
    parser.add_argument('--check', '-c', action='store_true', help='Check model assignments')
    parser.add_argument('--generate', '-g', action='store_true', help='Generate leaderboards')

    args = parser.parse_args()

    if args.interactive:
        interactive_main()
    elif args.check:
        check_models()
    elif args.generate:
        generate_leaderboard()
    else:

        import sys
        if sys.stdin.isatty():  
            interactive_main()
            generate_leaderboard()
        else:

            check_models()
            generate_leaderboard()

if __name__ == "__main__":
    main()
