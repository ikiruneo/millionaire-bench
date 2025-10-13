import json
import os
import re
import math
from collections import defaultdict
from statistics import mean, stdev

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
    print(f"Finding the median result file for each model in {results_dir} based on average winnings...")
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

def main():
    # Process local models
    local_data = process_results_directory('../results')
    with open('leaderboard_local.json', 'w', encoding='utf-8') as f:
        json.dump(local_data, f, indent=2, ensure_ascii=False)
    print(f"Local leaderboard data saved to leaderboard_local.json")
    print(f"Processed {len(local_data['models'])} local models")
    print(f"Global maximum value: {local_data['global_max_value']:,}€")

    # Process cloud models
    cloud_data = process_results_directory('../results/cloud')
    with open('leaderboard_cloud.json', 'w', encoding='utf-8') as f:
        json.dump(cloud_data, f, indent=2, ensure_ascii=False)
    print(f"Cloud leaderboard data saved to leaderboard_cloud.json")
    print(f"Processed {len(cloud_data['models'])} cloud models")
    print(f"Global maximum value: {cloud_data['global_max_value']:,}€")

    # Also create the original combined file for backward compatibility
    all_models = local_data['models'] + cloud_data['models']
    all_models.sort(key=lambda x: x['median_value'], reverse=True)
    for i, model_info in enumerate(all_models):
        model_info['rank'] = i + 1
    combined_data = {
        'models': all_models,
        'global_max_value': max(local_data['global_max_value'], cloud_data['global_max_value'])
    }
    with open('leaderboard_data.json', 'w', encoding='utf-8') as f:
        json.dump(combined_data, f, indent=2, ensure_ascii=False)
    print(f"Combined leaderboard data saved to leaderboard_data.json")
    print(f"Processed {len(all_models)} total models")
    print(f"\nLocal models by median value of averages:")
    for i, model_info in enumerate(local_data['models']):
        low_dev = model_info['low_deviation_euros'] if model_info['low_deviation_euros'] is not None else 'N/A'
        high_dev = model_info['high_deviation_euros'] if model_info['high_deviation_euros'] is not None else 'N/A'
        print(f"{i+1}. {model_info['model_name']}: median value={model_info['median_value']:.0f}, deviations: -{low_dev}€/+{high_dev}€")
    print(f"\nCloud models by median value of averages:")
    for i, model_info in enumerate(cloud_data['models']):
        low_dev = model_info['low_deviation_euros'] if model_info['low_deviation_euros'] is not None else 'N/A'
        high_dev = model_info['high_deviation_euros'] if model_info['high_deviation_euros'] is not None else 'N/A'
        print(f"{i+1}. {model_info['model_name']}: median value={model_info['median_value']:.0f}, deviations: -{low_dev}€/+{high_dev}€")

if __name__ == "__main__":
    main()