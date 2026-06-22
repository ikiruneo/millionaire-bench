#!/usr/bin/env python3
import json
import urllib.request
import urllib.error
import time
import os
import re
import threading
import itertools
import subprocess
import sys
import socket

SERVER_URL = "http://localhost:1234" # e.g. https://openrouter.ai/api (/v1 not needed).
API_KEY = "sk-xxx"
MODEL_NAME = "model-name-here"

SYSTEM_PROMPT = "Du bist ein Kandidat bei 'Wer wird Millionär'. Wähle die richtige Antwort aus den vier Optionen. Antworte AUSCHLIESSLICH mit einem einzigen Buchstaben: A, B, C oder D. Keine andere Erklärung, nur der Buchstabe! Beispiel: Wenn A die richtige Antwort ist, antworte nur: A"
FAIL_CHARS = "123456789ABCDEF"
PRIZE_LEVELS = ["50€", "100€", "200€", "300€", "500€", "1.000€", "2.000€", "4.000€", "8.000€", "16.000€", "32.000€", "64.000€", "125.000€", "500.000€", "1.000.000€"]
PRIZE_AMOUNTS = {i + 1: amount for i, amount in enumerate(PRIZE_LEVELS)}
AMOUNT_MAPPING_INT = {amount: int(amount.replace('€', '').replace('.', '')) for amount in PRIZE_LEVELS}
AMOUNT_MAPPING_INT["0€"] = 0


def _spinner_animation(stop_event):
    for char in itertools.cycle(['-', '\\', '|', '/']):
        if stop_event.is_set():
            break
        print(char, end='\b', flush=True)
        time.sleep(0.2)


def mean_to_prize(rounds):
    if not rounds: return "0€"
    corrects = [r["correct_answers"] for r in rounds]
    mc = sum(corrects) / len(corrects)
    floor_lvl = int(mc)
    frac = mc - floor_lvl
    prizes = [0] + [AMOUNT_MAPPING_INT[p] for p in PRIZE_LEVELS]
    p_floor = prizes[floor_lvl]
    p_ceil = prizes[min(floor_lvl + 1, 15)]
    prize = p_floor + (p_ceil - p_floor) * frac
    return f"{prize:,.0f}€".replace(",", ".") if prize >= 1000 else f"{int(prize)}€"

header = f"""
Wer wird Millionär? Benchmark
=====================================
Model:    {MODEL_NAME}
URL:      {SERVER_URL}
-------------------------------------"""
print(header)

try:
    with open("fragen_antworten.json", 'r', encoding='utf-8') as f:
        questions = json.load(f)
except (FileNotFoundError, json.JSONDecodeError) as e:
    print(f"Error loading questions: {e}")
    exit(1)

verbose_mode = input("Show full LLM response? [y/N] ").strip().lower() in ['y', 'yes']

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
        
        spinner_thread = threading.Thread(target=_spinner_animation, args=(stop_event,))
        spinner_thread.start()
        
        try:
            data = {"model": MODEL_NAME, "messages": [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": prompt}], "stream": False}
            headers = {"Authorization": f"Bearer {API_KEY}", "User-Agent": "millionaire-bench/1.0"} if API_KEY else {"User-Agent": "millionaire-bench/1.0"}
            req = urllib.request.Request(
                f"{SERVER_URL}/v1/chat/completions",
                data=json.dumps(data).encode("utf-8"),
                headers={**headers, "Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=300) as resp:
                response_data = json.loads(resp.read().decode("utf-8"))
                if choices := response_data.get("choices"):
                    response_content = choices[0].get("message", {}).get("content", "").strip()
                    if verbose_mode:
                        full_response = response_content
                    letters = re.findall(r'\b[A-D]\b', response_content, re.IGNORECASE)
                    llm_answer = letters[-1].upper() if letters else "INVALID"
                else:
                    llm_answer = "ERROR"
                    if verbose_mode:
                        full_response = ""
        except (urllib.error.URLError, socket.timeout, OSError):
            llm_answer = "ERROR"
            if verbose_mode:
                full_response = ""
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
                if verbose_mode:
                    print(f"└─ Failed at Level {current_level}")
                    q_limit = 70
                    display_q = f"{question_text[:q_limit]}..." if len(question_text) > q_limit else question_text
                    print(f"   ├─ Q: {display_q}")
                    print(f"   ├─ LLM Answer: '{llm_answer}'")
                    print(f"   ├─ Correct is: '{correct_letter}'")
                    print(f"   └─ Full Response: '{full_response}'")
                break
        except ValueError:
            print("E]", flush=True)
            if verbose_mode:
                q_limit = 50
                display_q = f"{question_text[:q_limit]}..." if len(question_text) > q_limit else question_text
                print(f"└─ Error: Correct answer '{correct_answer}' not in options for Q: {display_q}")
                print(f"   └─ Full Response: '{full_response}'")
            break
            
    if correct_answers == 15:
        print("✓]", flush=True)
    
    results.append({"correct_answers": correct_answers})
prize = mean_to_prize(results)
million_wins = sum(1 for r in results if r["correct_answers"] == 15)
results_data = {"model": MODEL_NAME, "rounds": results, "score": prize, "million_wins": million_wins}

print(f"\nScore: {prize} | Million Wins: {million_wins}")

if "localhost" in SERVER_URL or "127.0.0.1" in SERVER_URL:
    default_dir = "local"
else:
    default_dir = "cloud"

print(f"\nServer URL suggests saving in results/{default_dir}/")
save_choice = input(f"Save result in results/{default_dir}? (Y/n): ").strip().lower()

if save_choice in ['n', 'no']:
    save_option = input("Do not save=1, Save in results/cloud=2 (1/2): ").strip()
    if save_option == "2":
        results_dir = os.path.join("results", "cloud")
    elif save_option == "1":
        results_dir = None
    else:
        results_dir = os.path.join("results", "cloud")
else:
    results_dir = os.path.join("results", default_dir)

if results_dir:
    os.makedirs(results_dir, exist_ok=True)
    base_filename = f"result_{MODEL_NAME.replace('/', '-')}.json"
    result_filename = os.path.join(results_dir, base_filename)
    counter = 2
    while os.path.exists(result_filename):
        result_filename = os.path.join(results_dir, f"{base_filename.rsplit('.', 1)[0]}_{counter}.json")
        counter += 1

    with open(result_filename, 'w', encoding='utf-8') as f:
        json.dump(results_data, f, indent=2, ensure_ascii=False)
else:
    result_filename = None
    print("Results not saved.")

if result_filename:
    print(f"Saved results to: {result_filename}")
else:
    print("Results not saved to file.")

update_leaderboard = input("\nWant to update the Leaderboard? [Y/n] ").strip().lower()
if update_leaderboard in ['y', 'yes', '']:
    try:
        subprocess.run([sys.executable, "update.py"], 
                       cwd="leaderboard", check=True, stdin=None, stdout=None, stderr=None)
        print("Leaderboard updated successfully!")
    except subprocess.CalledProcessError as e:
        print("Error running leaderboard update script.")
        print("Return code:", e.returncode)
    except FileNotFoundError:
        print("Python not found. Please ensure Python is installed to update the leaderboard.")
