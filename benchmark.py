#!/usr/bin/env python3
import json
import requests
import time
import os
import re
import threading
import itertools
from statistics import median

SYSTEM_PROMPT = "Du bist ein Kandidat bei 'Wer wird Millionär'. Wähle die richtige Antwort aus den vier Optionen. Antworte AUSCHLIESSLICH mit einem einzigen Buchstaben: A, B, C oder D. Keine andere Erklärung, nur der Buchstabe! Beispiel: Wenn A die richtige Antwort ist, antworte nur: A"
SERVER_URL = "http://localhost:8000"
API_KEY = ""
MODEL_NAME = "lfm2:8b-a1b"
TEMPERATURE = 0.3
TOP_K = 40
TOP_P = 0.95
FAIL_CHARS = "123456789ABCDEF"

PRIZE_LEVELS = ["50€", "100€", "200€", "300€", "500€", "1.000€", "2.000€", "4.000€", "8.000€", "16.000€", "32.000€", "64.000€", "125.000€", "500.000€", "1.000.000€"]
PRIZE_AMOUNTS = {i + 1: amount for i, amount in enumerate(PRIZE_LEVELS)}
AMOUNT_MAPPING_INT = {amount: int(amount.replace('€', '').replace('.', '')) for amount in PRIZE_LEVELS}
AMOUNT_MAPPING_INT["0€"] = 0

def calculate_average_amount(rounds):
    if not rounds: return "0€"
    total = sum(AMOUNT_MAPPING_INT[PRIZE_AMOUNTS.get(r["correct_answers"], "0€")] for r in rounds)
    average = total / len(rounds)
    return f"{average:,.0f}€".replace(",", ".") if average >= 1000 else f"{int(average)}€"

def calculate_median_amount(rounds):
    if not rounds: return "0€"
    amounts = [AMOUNT_MAPPING_INT[PRIZE_AMOUNTS.get(r["correct_answers"], "0€")] for r in rounds]
    median_amount = median(amounts)
    return f"{median_amount:,.0f}€".replace(",", ".") if median_amount >= 1000 else f"{int(median_amount)}€"

model_name = MODEL_NAME
header = f"""
Wer wird Millionär? Benchmark
==================================================
Model:  {model_name}
URL:    {SERVER_URL}
Sampling: T:{TEMPERATURE}, P:{TOP_P}, K:{TOP_K}
--------------------------------------------------"""
print(header)

try:
    with open("fragen_antworten.json", 'r', encoding='utf-8') as f:
        questions = json.load(f)
except (FileNotFoundError, json.JSONDecodeError) as e:
    print(f"Error loading questions: {e}")
    exit(1)

print("Press Enter to start...")
input()

session = requests.Session()
results = []

for question_num in range(1, 46):
    current_level = 1
    correct_answers = 0
    
    print(f"Game {question_num:02d}/45: [", end="", flush=True)
    
    while current_level <= 15:
        question_data = questions.get(str(current_level), [[]])[question_num - 1]
        if not question_data: continue

        question_text, *options, correct_answer = question_data
        prompt = f"{question_text}\n" + "\n".join(f"{chr(65+i)}: {opt}" for i, opt in enumerate(options))
        
        stop_event = threading.Event()
        def _spinner_animation():
            for char in itertools.cycle(['-', '\\', '|', '/']):
                if stop_event.is_set(): break
                print(char, end='\b', flush=True)
                time.sleep(0.2)
        
        spinner_thread = threading.Thread(target=_spinner_animation)
        spinner_thread.start()
        
        start_time = time.time()
        
        try:
            data = {"model": model_name, "messages": [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": prompt}], "stream": False, "temperature": TEMPERATURE, "top_k": TOP_K, "top_p": TOP_P}
            headers = {"Authorization": f"Bearer {API_KEY}"} if API_KEY else {}
            response = session.post(f"{SERVER_URL}/v1/chat/completions", json=data, headers=headers, timeout=300)
            if response.status_code == 200 and (choices := response.json().get("choices")):
                response_content = choices[0].get("message", {}).get("content", "").strip()
                letters = re.findall(r'\b[A-D]\b', response_content, re.IGNORECASE)
                llm_answer = letters[-1].upper() if letters else "INVALID"
            else:
                llm_answer = "ERROR"
        except requests.exceptions.RequestException:
            llm_answer = "ERROR"
        finally:
            stop_event.set()
            spinner_thread.join()
        
        try:
            correct_letter = chr(65 + options.index(correct_answer))
            if llm_answer == correct_letter:
                print(".", end="", flush=True)
                correct_answers += 1
                current_level += 1
            else:
                fail_char = FAIL_CHARS[current_level - 1]
                print(f"{fail_char}]", flush=True)
                print(f"  └─ Failed at Level {current_level}")
                q_limit = 70
                display_q = f"{question_text[:q_limit]}..." if len(question_text) > q_limit else question_text
                print(f"     ├─ Q: {display_q}")
                print(f"     ├─ LLM Answer: '{llm_answer}'")
                print(f"     └─ Correct is: '{correct_letter}'")
                break
        except ValueError:
            print("E]", flush=True)
            q_limit = 50
            display_q = f"{question_text[:q_limit]}..." if len(question_text) > q_limit else question_text
            print(f"  └─ Error: Correct answer '{correct_answer}' not in options for Q: {display_q}")
            break
            
    if correct_answers == 15:
        print("✓]", flush=True)
    
    results.append({"correct_answers": correct_answers})

average_amount = calculate_average_amount(results)
median_amount = calculate_median_amount(results)
million_wins = sum(1 for r in results if r["correct_answers"] == 15)
results_data = {"model": model_name, "model_parameters": {"temperature": TEMPERATURE, "top_k": TOP_K, "top_p": TOP_P}, "rounds": results, "average_final_amount": average_amount, "median_final_amount": median_amount, "million_wins": million_wins}

base_filename = f"result_{model_name.replace('/', '-')}.json"
result_filename = base_filename
counter = 2
while os.path.exists(result_filename):
    result_filename = f"{base_filename.rsplit('.', 1)[0]}_{counter}.json"
    counter += 1

with open(result_filename, 'w', encoding='utf-8') as f:
    json.dump(results_data, f, indent=2, ensure_ascii=False)

print(f"\nAverage Amount: {average_amount} | Million Wins: {million_wins}")
print(f"T:{TEMPERATURE}, K:{TOP_K}, P:{TOP_P}")
print(f"Saved results to: {result_filename}")
