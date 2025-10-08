# "Wer wird Millionär?" LLM Benchmark

 i have created a benchmark for german "who wants to be millionaire" questions. there are 45x15 questions, all 45 rounds go from easy to hard and all tested models ran through all 45 rounds and got kicked out of a round if the answer was wrong, keeping the current winnings. no jokers.

i am a bit limited with the selection of llm's since i run them on my framework laptop 13 (amd ryzen 5 7640u with 32 gb ram), so i mainly used smaller llm's. also, qwen3's thinking went on for way to long for each question so i just tested non-thinking models except for gpt-oss-20b (low). but in my initial testing for qwen3-4b-thinking-2507, it seemed to worsen the quality of answers at least for the first questions.

the first few questions are often word-play and idioms questions needing great understanding of the german language. these proved to be very hard for most llm's but are easily solvable by the average german. once the first few questions were solved the models had an easier time answering.

i tried to use optimal model settings and included them in the table, let me know if they could be improved. all models are quant Q4_K_M.

i have close to no python coding ability so the main script was created with qwen3-coder. the project (with detailed results for each model, and the queationaire) is open souce and available on github.

## Usage

1. The benchmark.py should work with local LLM servers like LM Studio and any other OpenAI API compatible URL.

2. Edit the benchmark.json, change `SERVER_URL`, add `API_KEY` (if needed), set `MODEL_NAME` and sampling parameters.

3. Run the benchmark script:
   
   ```bash
   python3 benchmark.py
   ```

note: `benchmark_2.py` offers a more advanced implementation that goes right over my head, written by people more knowledgeable than i am. from what I understand, it's better suited for cloud-based URLs and offers concurrency and safer answer parsing.

## Benchmark Results

### Local

| Model Name                 | Total | Active | Thinking | Wins | Median | Average   |
| -------------------------- | ----- | ------ | -------- | ---- | ------ | --------- |
| mistral‑small‑3.2          | 24 B  | 24 B   | No       | 2    | 500 €  | 63.812 €  |
| qwen3‑30b‑a3b‑2507         | 30 B  | 3 B    | No       | 5    | 200 €  | 118.111 € |
| phi‑4                      | 14 B  | 14 B   | No       | 1    | 200 €  | 25.987 €  |
| magistral‑small‑2509       | 24 B  | 24 B   | No       | 0    | 200 €  | 25.003 €  |
| gpt‑oss‑20b                | 21 B  | 4 B    | Low      | 3    | 100 €  | 80.177 €  |
| mistral‑nemo‑instruct‑2407 | 12 B  | 12 B   | No       | 1    | 100 €  | 34.383 €  |
| qwen3‑4b‑thinking‑2507     | 4 B   | 4 B    | Yes      | 1    | 100 €  | 27.343 €  |
| gemma‑3‑12b                | 12 B  | 12 B   | No       | 1    | 100 €  | 24.291 €  |
| gemma‑3‑27b                | 27 B  | 27 B   | No       | 0    | 100 €  | 15.039 €  |
| hermes‑4‑14b               | 14 B  | 14 B   | No       | 0    | 100 €  | 14.916 €  |
| apertus:8b                 | 8 B   | 8 B    | No       | 0    | 100 €  | 1.998 €   |
| granite‑4.0‑h‑small        | 32 B  | 9 B    | No       | 0    | 100 €  | 764 €     |
| granite‑3.2‑8b             | 8 B   | 8 B    | No       | 0    | 100 €  | 620 €     |
| qwen3‑4b‑2507              | 4 B   | 4 B    | No       | 0    | 50 €   | 624 €     |
| llama‑3.1‑8b‑instruct      | 8 B   | 8 B    | No       | 0    | 50 €   | 484 €     |
| gemma‑3n‑e4b               | 8 B   | 4 B    | No       | 0    | 50 €   | 383 €     |
| qwen3‑1.7b‑thinking        | 1.7 B | 1.7 B  | Yes      | 0    | 50 €   | 356 €     |
| granite‑4‑h‑tiny           | 7 B   | 1 B    | No       | 0    | 50 €   | 321 €     |
| lfm2:8b‑a1b                | 8 B   | 1.5 B  | No       | 0    | 50 €   | 303 €     |
| gemma‑3‑4b                 | 4 B   | 4 B    | No       | 0    | 50 €   | 158 €     |
| lfm2‑2.6b                  | 2.6 B | 2.6 B  | No       | 0    | 50 €   | 126 €     |
| granite‑4.0‑h‑micro        | 3 B   | 3 B    | No       | 0    | 50 €   | 100 €     |
| ai21-jamba-reasoning-3b    | 3B    | 3B     | Yes      | 0    | 0€     | 225€      |
| phi‑4‑mini‑instruct        | 3 B   | 3 B    | No       | 0    | 0 €    | 157 €     |
| llama‑3.2‑3b‑instruct      | 3 B   | 3 B    | No       | 0    | 0 €    | 125 €     |
| ministral‑8b‑instruct‑2410 | 8 B   | 8 B    | No       | 0    | 0 €    | 60 €      |
| qwen3‑1.7b                 | 1.7 B | 1.7 B  | No       | 0    | 0 €    | 57 €      |

*Average* is the median average out of five runs, often less runs for big or thinking models due to resource limitation (one run can take multiple hours). human average winnings of the first 999 shows is 36.000€ ([source](https://www.stern.de/kultur/tv/jubilaeum-von--wer-wird-millionaer---zahlen-und-fakten-aus-999-ausgaben-3605146.html)).

### Cloud

| Model Name                     | Total  | Active | Wins | Median      | Average   |
| ------------------------------ | ------ | ------ | ---- | ----------- | --------- |
| gpt‑5 (medium)                 | N/A    | N/A    | 36   | 1.000.000 € | 813.783 € |
| gemini‑2.5‑pro                 | N/A    | N/A    | 33   | 1.000.000 € | 742.004 € |
| o3 (medium)                    | N/A    | N/A    | 31   | 1.000.000 € | 716.546 € |
| gpt‑5‑mini (medium)            | N/A    | N/A    | 31   | 1.000.000 € | 673.838 € |
| o4‑mini (medium)               | N/A    | N/A    | 21   | 500.000 €   | 512.221 € |
| glm‑4.5‑FP8                    | 355 B  | 32 B   | 17   | 64.000 €    | 410.813 € |
| qwen3‑235b‑a22b                | 235 B  | 22 B   | 15   | 64.000 €    | 369.027 € |
| gpt‑4o                         | N/A    | N/A    | 12   | 16.000 €    | 302.186 € |
| gpt‑5‑nano (medium)            | N/A    | N/A    | 12   | 16.000 €    | 299.494 € |
| gemini‑2.5‑flash               | N/A    | N/A    | 7    | 16.000 €    | 205.816 € |
| gpt‑5‑nano (minimal)           | N/A    | N/A    | 11   | 8 000 €     | 277.661 € |
| gpt‑4.1                        | N/A    | N/A    | 10   | 8 000 €     | 256.073 € |
| deepseek-chat‑v3‑0324          | 67.1 B | 67.1 B | 6    | 4 000 €     | 161.492 € |
| gpt‑oss‑120b                   | 120 B  | 120 B  | 11   | 2 000 €     | 275.564 € |
| qwq‑32b                        | 32 B   | 32 B   | 8    | 2 000 €     | 197.799 € |
| c4ai‑command‑a‑03‑2025         | 111 B  | 111 B  | 6    | 2 000 €     | 155.636 € |
| kimi‑k2                        | 1 T    | 32 B   | 4    | 2 000 €     | 125.136 € |
| gpt‑4.1‑mini                   | N/A    | N/A    | 3    | 2 000 €     | 113.616 € |
| qwen3‑235b‑a22b‑2507           | 235 B  | 22 B   | 7    | 1 000 €     | 163.144 € |
| gpt‑4o‑mini                    | N/A    | N/A    | 2    | 1 000 €     | 74.698 €  |
| gpt‑5‑mini (minimal)           | N/A    | N/A    | 1    | 1 000 €     | 53.618 €  |
| llama‑4‑maverick               | 400 B  | 18 B   | 6    | 500 €       | 161.411 € |
| deepseek-chat‑v3.1             | 68.5 B | 68.5 B | 6    | 500 €       | 142.581 € |
| gemini‑2.5‑flash‑lite          | N/A    | N/A    | 2    | 500 €       | 63.107 €  |
| mistral‑small‑3.2‑24b‑instruct | 24 B   | 24 B   | 1    | 500 €       | 41.017 €  |
| glm‑4.5‑air‑FP8                | N/A    | N/A    | 0    | 300 €       | 281.459 € |
| Behemoth‑123B‑v1.2             | N/A    | N/A    | 3    | 300 €       | 84.963 €  |
| gpt‑4.1‑nano                   | N/A    | N/A    | 1    | 300 €       | 37.838 €  |
| gemma‑3‑27b‑it                 | 27 B   | 27 B   | 0    | 300 €       | 7.634 €   |
| qwen3‑coder                    | 480 B  | 480 B  | 4    | 200 €       | 92.022 €  |
| llama‑3.3‑70b‑instruct         | 70 B   | 70 B   | 2    | 200 €       | 58.309 €  |
| gpt‑5‑nano (minimal)           | N/A    | N/A    | 0    | 100 €       | 2.324 €   |
| phi‑4                          | 14 B   | 14 B   | 0    | 50 €        | 1.892 €   |
| llama‑3.2‑1b‑instruct          | 1 B    | 1 B    | 0    | 0 €         | 155 €     |
| llama‑3.2‑3b‑instruct          | 3 B    | 3 B    | 0    | 0 €         | 121 €     |

1 run only. thanks to the reddit users `FullOf_Bad_Ideas` and `Pauli1_Go` for their help.

### Different quant tests

| Model Name             | Q4_K_M | Q8_0 | Difference |
| ---------------------- | ------ | ---- | ---------- |
| qwen3-4b-instruct-2507 | 624€   | 705€ | +13%       |
| gemma-3-4b             | 103€   | 141€ | +36%       |
| llama-3.2-3b-instruct  | 104€   | 78€  | -25%       |

ran every test 3 times and picked the median. results are very inconsistent for small models (±50%)

## Rules

- 45 unique rounds
- if lost, current winnings are kept
- no jokers

## Resources

Questions: https://github.com/GerritKainz/wer_wird_millionaer
