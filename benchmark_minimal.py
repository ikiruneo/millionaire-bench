#!/usr/bin/env python3
import json
import requests
import time
import os

# Configuration
SYSTEM_PROMPT = "You are a contestant on 'Who Wants to Be a Millionaire' and must answer questions in German. Think carefully and choose the best answer from the four options. Answer EXCLUSIVELY with a single letter: A, B, C or D. No other explanation, just the letter! Example: If A is the correct answer, answer only: A"
LLM_SERVER_URL = "http://localhost:1234/v1/chat/completions"
TEMPERATURE = 1
TOP_P = 0.95
TOP_K = 64

# Prize amounts
PRIZE_AMOUNTS = {
    1: "50€", 2: "100€", 3: "200€", 4: "300€", 5: "500€",
    6: "1.000€", 7: "2.000€", 8: "4.000€", 9: "8.000€", 10: "16.000€",
    11: "32.000€", 12: "64.000€", 13: "125.000€", 14: "500.000€", 15: "1.000.000€"
}

def get_active_model():
    try:
        response = requests.get("http://localhost:1234/v1/models", timeout=10)
        if response.status_code == 200:
            models_data = response.json()
            if "data" in models_data and len(models_data["data"]) > 0:
                return models_data["data"][0]["id"]
    except:
        pass
    return "unknown-model"

def calculate_average_amount(rounds):
    if not rounds:
        return "0€"
    
    amount_mapping = {
        "0€": 0, "50€": 50, "100€": 100, "200€": 200, "300€": 300,
        "500€": 500, "1.000€": 1000, "2.000€": 2000, "4.000€": 4000,
        "8.000€": 8000, "16.000€": 16000, "32.000€": 32000, "64.000€": 64000,
        "125.000€": 125000, "500.000€": 500000, "1.000.000€": 1000000
    }
    
    total = sum(amount_mapping[round_data["final_amount"]] for round_data in rounds)
    average = total / len(rounds)
    
    if average >= 1000000:
        return f"{average:,.1f}€".replace(",", ".")
    elif average >= 1000:
        return f"{average:,.0f}€".replace(",", ".")
    else:
        return f"{int(average)}€"

print("\nWho Wants to Be a Millionaire? Benchmark")
print("=" * 50)

# Get model info
model_name = get_active_model()
print(f"Active Model: {model_name}")
print(f"Server: {LLM_SERVER_URL}")
print(f"Parameters: T:{TEMPERATURE}, P:{TOP_P}, K:{TOP_K}")
print("-" * 50)

# Load questions
try:
    with open("fragen_antworten.json", 'r', encoding='utf-8') as f:
        questions = json.load(f)
except Exception as e:
    print(f"Error loading questions: {e}")
    exit(1)

# Wait for user to press enter
print("Press Enter to start...")
input()

# Run all 45 games automatically
results = []
print("-" * 30)

for question_num in range(1, 46):
    current_level = 1
    correct_answers = 0
    
    while current_level <= 15:
        if str(current_level) not in questions:
            print(f"Error: No questions for level {current_level}")
            break
            
        level_questions = questions[str(current_level)]
        
        if question_num > len(level_questions):
            print(f"Error: Question #{question_num} does not exist in level {current_level}")
            break
            
        question_data = level_questions[question_num-1]
        question_text = question_data[0]
        options = question_data[1:5]
        correct_answer = question_data[5]
        print(f"\nQuestion {current_level:02d}/15, Run {question_num}/45 - {PRIZE_AMOUNTS[current_level]}")
        print(f"Q: {question_text}")
        print(f"A: {options[0]}")
        print(f"B: {options[1]}")
        print(f"C: {options[2]}")
        print(f"D: {options[3]}")
        
        # Format prompt
        prompt = f"{question_text}\nA: {options[0]}\nB: {options[1]}\nC: {options[2]}\nD: {options[3]}"
        
        # Get LLM response
        print("\nWaiting for response...")
        start_time = time.time()
        
        try:
            data = {
                "model": model_name,
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                "stream": False,
                "temperature": TEMPERATURE,
                "top_p": TOP_P,
                "top_k": TOP_K
            }
            
            response = requests.post(LLM_SERVER_URL, json=data, timeout=300)
            if response.status_code == 200:
                result = response.json()["choices"][0]["message"]["content"].strip()
                # Parse response
                if result.upper() in ['A', 'B', 'C', 'D']:
                    llm_answer = result.upper()
                else:
                    # Try to find a letter in the response
                    llm_answer = "INVALID"
                    for char in result:
                        if char.upper() in ['A', 'B', 'C', 'D']:
                            llm_answer = char.upper()
                            break
            else:
                llm_answer = "ERROR"
        except Exception as e:
            llm_answer = "ERROR"
        
        response_time = time.time() - start_time
        print(f"answer given: {llm_answer} (in {response_time:.2f} seconds)")
        
        # Check correct answer
        try:
            correct_index = options.index(correct_answer)
            correct_letter = ['A', 'B', 'C', 'D'][correct_index]
        except ValueError:
            print(f"Error: Correct answer '{correct_answer}' not found in options")
            break
        
        print(f"Correct answer: {correct_letter} ({correct_answer})")
        
        # Check if answer is correct
        if llm_answer == correct_letter:
            print("✓ Correct!")
            correct_answers += 1
            current_level += 1
        else:
            print("✗ Wrong!")
            break
    
    results.append({
        "correct_answers": correct_answers,
        "final_amount": PRIZE_AMOUNTS[correct_answers] if correct_answers > 0 else "0€",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    })

# Calculate statistics
average_amount = calculate_average_amount(results)
million_wins = sum(1 for r in results if r["correct_answers"] == 15)

# Prepare results data
results_data = {
    "model": model_name,
    "model_parameters": {
        "temperature": TEMPERATURE,
        "top_p": TOP_P,
        "top_k": TOP_K
    },
    "rounds": results,
    "average_final_amount": average_amount,
    "million_wins": million_wins
}

safe_model_name = model_name.replace("/", "-")
result_filename = f"result_{safe_model_name}.json"

if os.path.exists(result_filename):
    counter = 2
    while os.path.exists(f"result_{safe_model_name}_{counter}.json"):
        counter += 1
    result_filename = f"result_{safe_model_name}_{counter}.json"

with open(result_filename, 'w', encoding='utf-8') as f:
    json.dump(results_data, f, indent=2, ensure_ascii=False)

print(f"\naverage_amount: {average_amount}")
print(f"million_wins: {million_wins}")
print(f"parameters: T:{TEMPERATURE}, P:{TOP_P}, K:{TOP_K}")
print(f"saved as: {result_filename}")
