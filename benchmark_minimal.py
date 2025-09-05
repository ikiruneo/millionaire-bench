#!/usr/bin/env python3
import json
import requests
import time
import os
import re

SYSTEM_PROMPT = "Du bist ein Kandidat bei 'Wer wird Millionär' und musst Fragen auf Deutsch beantworten. Wähle die richtige Antwort aus den vier Optionen. Antworte AUSCHLIESSLICH mit einem einzigen Buchstaben: A, B, C oder D. Keine andere Erklärung, nur der Buchstabe! Beispiel: Wenn A die richtige Antwort ist, antworte nur: A"
LLM_SERVER_URL = "http://localhost:1234/v1/chat/completions"
TEMPERATURE = 0.8
TOP_P = 0.95
TOP_K = 40

PRIZE_LEVELS = [
    "50€", "100€", "200€", "300€", "500€", "1.000€", "2.000€", "4.000€", 
    "8.000€", "16.000€", "32.000€", "64.000€", "125.000€", "500.000€", "1.000.000€"
]
PRIZE_AMOUNTS = {i + 1: amount for i, amount in enumerate(PRIZE_LEVELS)}
AMOUNT_MAPPING_INT = {amount: int(amount.replace('€', '').replace('.', '')) for amount in PRIZE_LEVELS}
AMOUNT_MAPPING_INT["0€"] = 0

def get_active_model():
    try:
        response = requests.get("http://localhost:1234/v1/models", timeout=10)
        if response.status_code == 200:
            models_data = response.json()
            if "data" in models_data and len(models_data["data"]) > 0:
                return models_data["data"][0]["id"]
    except requests.exceptions.RequestException:
        pass
    return "unknown-model"

def calculate_average_amount(rounds):
    if not rounds:
        return "0€"
    
    total = sum(AMOUNT_MAPPING_INT[round_data["final_amount"]] for round_data in rounds)
    average = total / len(rounds)
    
    if average >= 1000:
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
except FileNotFoundError:
    print("Error: fragen_antworten.json not found.")
    exit(1)
except json.JSONDecodeError:
    print("Error: Could not decode fragen_antworten.json. Please check the file format.")
    exit(1)

print("Press Enter to start...")
input()

session = requests.Session()
results = []
print("-" * 30)

for question_num in range(1, 46):
    current_level = 1
    correct_answers = 0
    
    while current_level <= 15:
        question_data = questions.get(str(current_level), [])[question_num-1]
        
        question_text = question_data[0]
        options = question_data[1:5]
        correct_answer = question_data[5]
        print(f"\nQuestion {current_level:02d}/15, Run {question_num}/45 - {PRIZE_AMOUNTS[current_level]}")
        print(f"Q: {question_text}")
        for i, option in enumerate(options):
            print(f"{chr(65+i)}: {option}")
        
        prompt = f"{question_text}\n" + "\n".join(f"{chr(65+i)}: {option}" for i, option in enumerate(options))
        
        print("\nWaiting for response...")
        start_time = time.time()
        
        try:
            data = {
                "model": model_name,
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                "stream": False, "temperature": TEMPERATURE, "top_p": TOP_P, "top_k": TOP_K
            }
            
            response = session.post(LLM_SERVER_URL, json=data, timeout=300)
            if response.status_code == 200:
                response_content = response.json()["choices"][0]["message"]["content"].strip()
            
                answer_part = response_content.split('</think>', 1)[-1]
            
                match = re.search(r'\b[A-D]\b', answer_part, re.IGNORECASE)
                
                if match:
                    llm_answer = match.group(0).upper()
                else:
                    llm_answer = "INVALID"
                    
            else:
                llm_answer = "ERROR"
        except requests.exceptions.RequestException:
            llm_answer = "ERROR"
        
        response_time = time.time() - start_time
        print(f"answer given: {llm_answer} (in {response_time:.2f} seconds)")
        
        try:
            correct_index = options.index(correct_answer)
            correct_letter = ['A', 'B', 'C', 'D'][correct_index]
        except ValueError:
            print(f"Error: Correct answer '{correct_answer}' not found in options")
            break
        
        print(f"Correct answer: {correct_letter} ({correct_answer})")
        
        if llm_answer == correct_letter:
            print("✓ Correct!")
            correct_answers += 1
            current_level += 1
        else:
            print("✗ Wrong!")
            break
    
    final_amount = PRIZE_AMOUNTS.get(correct_answers, "0€")
    results.append({
        "correct_answers": correct_answers,
        "final_amount": final_amount,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    })

average_amount = calculate_average_amount(results)
million_wins = sum(1 for r in results if r["correct_answers"] == 15)

results_data = {
    "model": model_name,
    "model_parameters": {"temperature": TEMPERATURE, "top_p": TOP_P, "top_k": TOP_K},
    "rounds": results,
    "average_final_amount": average_amount,
    "million_wins": million_wins
}

safe_model_name = model_name.replace("/", "-")
result_filename = f"result_{safe_model_name}.json"

counter = 1
base_filename = result_filename
while os.path.exists(result_filename):
    counter += 1
    result_filename = f"{os.path.splitext(base_filename)[0]}_{counter}.json"

with open(result_filename, 'w', encoding='utf-8') as f:
    json.dump(results_data, f, indent=2, ensure_ascii=False)

print(f"\naverage_amount: {average_amount}")
print(f"million_wins: {million_wins}")
print(f"parameters: T:{TEMPERATURE}, P:{TOP_P}, K:{TOP_K}")
print(f"saved as: {result_filename}")
