import json
import os
import re
import math
from collections import defaultdict
from statistics import mean, stdev

def get_model_name_from_filename(filename):
    """Extract model name from filename like 'result_modelname_x.json' or 'result_modelname.json'"""
    # Remove 'result_' prefix and '.json' suffix
    name = filename.replace('result_', '').replace('.json', '')
    # Remove run number suffixes like _2, _3, _4, _5, _6, _7, _8, _9, _10, etc. (but keep _0, _1 which are part of model names like @q8_0)
    # These higher numbers (>1) typically indicate different runs of the same model
    base_name = re.sub(r'_(2|3|4|5|6|7|8|9|10|11|12|13|14|15|16|17|18|19|20)$', '', name)
    return base_name

def convert_amount_to_numeric(amount_str):
    """Convert amount string like '1.998€' to numeric value, where '.' is a thousand separator"""
    # Remove the € symbol
    numeric_str = amount_str.replace('€', '')
    # Remove thousand separators (dots)
    numeric_str = numeric_str.replace('.', '')
    try:
        return float(numeric_str)
    except ValueError:
        # If conversion fails, return 0
        return 0.0

def map_correct_answers_to_prize(correct_answers):
    """Map correct answers to prize values"""
    prize_values = [
        "0€", "50€", "100€", "200€", "300€", "500€", 
        "1.000€", "2.000€", "4.000€", "8.000€", "16.000€", 
        "32.000€", "64.000€", "125.000€", "500.000€", "1.000.000€"
    ]
    
    # Cap at 15 (which maps to 1.000.000€)
    index = min(int(correct_answers), 15) if correct_answers >= 0 else 0
    return prize_values[index]

def convert_prize_to_numeric(prize_str):
    """Convert prize string like '1.000€' to numeric value"""
    numeric_str = prize_str.replace('€', '')
    numeric_str = numeric_str.replace('.', '')
    try:
        return int(numeric_str)
    except ValueError:
        return 0

def calculate_log_percentage(value):
    """Calculate percentage using fixed logarithmic scale where 1,000,000€ = 100%
    Formula: (Math.log(v + a) - Math.log(a)) / (Math.log(1_000_000 + a) - Math.log(a)) * 100
    where a = 50.00500050005
    """
    a = 50.00500050005
    max_value = 1_000_000
    
    # Calculate the logarithmic percentage
    log_value = (math.log(value + a) - math.log(a)) / (math.log(max_value + a) - math.log(a)) * 100
    return max(0, min(100, log_value))  # Clamp between 0 and 100

def main():
    results_dir = '../results'
    
    print("Finding the median result file for each model based on average winnings...")
    
    # First, gather all result files for each model
    model_files = defaultdict(list)
    
    for filename in os.listdir(results_dir):
        if filename.endswith('.json') and filename.startswith('result_') and not os.path.isdir(os.path.join(results_dir, filename)):
            filepath = os.path.join(results_dir, filename)
            
            with open(filepath, 'r', encoding='utf-8') as f:
                try:
                    data = json.load(f)
                    model_name = get_model_name_from_filename(filename)
                    
                    # Store all files for this model
                    model_files[model_name].append((filepath, filename))
                
                except json.JSONDecodeError:
                    print(f"Error decoding JSON in file: {filename}")
                    continue
    
    leaderboard_data = []
    all_average_scores = []  # Collect all average scores to find global maximum
    
    # For each model, process all result files to get 5 average values
    for model_name, files in model_files.items():
        if not files:
            continue
            
        # Process each result file for this model
        average_scores = []
        
        for filepath, filename in files:
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Extract correct answers from rounds
                rounds = data.get('rounds', [])
                correct_answers_list = [round_data.get('correct_answers', 0) for round_data in rounds]
                
                # Remove top 5 and bottom 5 correct_answers values
                sorted_answers = sorted(correct_answers_list)
                n = len(sorted_answers)
                
                if n > 10:  # Need more than 10 results to remove 5 from each end
                    middle_35_answers = sorted_answers[5 : n - 5]  # Remove 5 from each end
                else:
                    # If we have 10 or fewer results, keep all of them
                    middle_35_answers = sorted_answers
                
                # Convert correct answers to prize values and calculate the average in Euros
                if middle_35_answers:
                    # Convert each correct answer count to its prize value
                    prize_values = [map_correct_answers_to_prize(ca) for ca in middle_35_answers]
                    # Convert prize strings to numeric values
                    numeric_values = [convert_prize_to_numeric(prize) for prize in prize_values]
                    # Calculate the average in Euros
                    average_score = mean(numeric_values)
                else:
                    average_score = 0  # Fallback if no results
                    
                average_scores.append(average_score)
                all_average_scores.append(average_score)  # Collect for global maximum
                
            except json.JSONDecodeError:
                print(f"Error decoding JSON in file: {filename}")
                continue
            except Exception as e:
                print(f"Error processing file {filename}: {e}")
                continue
        
        # If we have average scores from multiple files, take the middle value
        if average_scores:
            sorted_averages = sorted(average_scores)
            n_averages = len(sorted_averages)
            
            if n_averages > 0:
                # Take the middle value of the averages
                middle_idx = n_averages // 2
                bar_value = sorted_averages[middle_idx]
                
                # Calculate error rates based on highest and lowest averages
                min_average = min(sorted_averages)
                max_average = max(sorted_averages)
                
                # Calculate absolute differences in Euros
                low_deviation_euros = round(bar_value - min_average)
                high_deviation_euros = round(max_average - bar_value)
                
                # For models with only 1 result file, set deviations to None
                if n_averages == 1:
                    low_deviation_euros = None
                    high_deviation_euros = None
            else:
                bar_value = 0
                low_deviation_percent = None
                high_deviation_percent = None
        else:
            bar_value = 0
            low_deviation_percent = None
            high_deviation_percent = None
        
        # Also get the median correct answer count for the model's name display
        # We'll use the first file for this (arbitrary choice)
        median_correct_answers = 0
        median_prize = "0€"
        
        if files:
            try:
                filepath, filename = files[0]
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Extract correct answers from rounds for median calculation
                rounds = data.get('rounds', [])
                correct_answers_list = [round_data.get('correct_answers', 0) for round_data in rounds]
                
                if correct_answers_list:
                    sorted_answers_for_median = sorted(correct_answers_list)
                    median_idx = len(sorted_answers_for_median) // 2
                    median_correct_answers = sorted_answers_for_median[median_idx]
                    median_prize = map_correct_answers_to_prize(median_correct_answers)
            except:
                pass
        
        # Get the average final amount from one of the files for comparison
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
            'median_correct_answers': median_correct_answers,
            'median_prize': median_prize,
            'bar_value': round(bar_value),  # This is the middle value of averages from multiple files
            'low_deviation_euros': low_deviation_euros,  # Absolute deviation in Euros to lower side
            'high_deviation_euros': high_deviation_euros,  # Absolute deviation in Euros to higher side
            'original_average': original_average,
            'log_percentage': float(f"{calculate_log_percentage(round(bar_value)):.1f}")  # Logarithmic percentage with 1 decimal place shown
        }
        
        leaderboard_data.append(model_info)
    
    # Find the global maximum value among all average scores
    global_max_value = max(all_average_scores) if all_average_scores else 1000000  # Default to 1M if no data
    
    # Sort by bar value in descending order
    sorted_leaderboard = sorted(leaderboard_data, key=lambda x: x['bar_value'], reverse=True)
    
    # Add ranking to each model and the global maximum
    for i, model_info in enumerate(sorted_leaderboard):
        model_info['rank'] = i + 1
        model_info['global_max_value'] = global_max_value  # Add global maximum for scaling
    
    # Write leaderboard data to JSON file in www directory
    with open('leaderboard_data.json', 'w', encoding='utf-8') as f:
        json.dump(sorted_leaderboard, f, indent=2, ensure_ascii=False)
    
    print(f"Leaderboard data saved to leaderboard_data.json")
    print(f"Processed {len(sorted_leaderboard)} models")
    print(f"Global maximum value: {global_max_value:,}€")
    
    # Display summary
    print("\nTop 10 performing models by middle value of averages:")
    for i, model_info in enumerate(sorted_leaderboard[:10]):
        low_dev = model_info['low_deviation_euros'] if model_info['low_deviation_euros'] is not None else 'N/A'
        high_dev = model_info['high_deviation_euros'] if model_info['high_deviation_euros'] is not None else 'N/A'
        print(f"{i+1}. {model_info['model_name']}: median answers={model_info['median_correct_answers']}, bar value={model_info['bar_value']:.0f}, deviations: -{low_dev}€/+{high_dev}€")

if __name__ == "__main__":
    main()
