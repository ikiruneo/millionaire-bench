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

| Model Name                 | Total Params | Active Params | Thinking | Million Wins | Average Winnings* |
| -------------------------- | ------------ | ------------- | -------- | ------------ | ----------------- |
| qwen3-30b-a3b-2507         | 30B          | 3B            | No       | 5            | 118.111€          |
| gpt-oss-20b                | 21B          | 4B            | Low      | 3            | 80.177€           |
| mistral-small-3.2          | 24B          | 24B           | No       | 2            | 63.812€           |
| human                      | N/A          | N/A           | Yes      | 0,15         | 36.000€           |
| mistral-nemo-instruct-2407 | 12B          | 12B           | No       | 1            | 34.383€           |
| qwen3-4b-2507              | 4B           | 4B            | Yes      | 1            | 27.343€           |
| phi-4                      | 14B          | 14B           | No       | 1            | 25.987€           |
| magistral-small-2509       | 24B          | 24B           | No       | 0            | 25.003€           |
| gemma-3-12b                | 12B          | 12B           | No       | 1            | 24.291€           |
| gemma-3-27b                | 27B          | 27B           | No       | 0            | 15.039€           |
| hermes-4-14b               | 14B          | 14B           | No       | 0            | 14.916€           |
| apertus-8b                 | 8B           | 8B            | No       | 0            | 1.998€            |
| granite-4.0-h-small        | 32B          | 9B            | No       | 0            | 764€              |
| qwen3-4b-2507              | 4B           | 4B            | No       | 0            | 624€              |
| granite-3.2-8b             | 8B           | 8B            | No       | 0            | 620€              |
| meta-llama-3.1-8b-instruct | 8B           | 8B            | No       | 0            | 484€              |
| gemma-3n-e4b               | 8B           | 4B            | No       | 0            | 383€              |
| qwen3-1.7b                 | 1.7B         | 1.7B          | Yes      | 0            | 356€              |
| granite-4-h-tiny           | 7B           | 1B            | No       | 0            | 321€              |
| lfm2-8b-a1b                | 8B           | 1.5B          | No       | 0            | 303€              |
| phi-4-mini-instruct        | 3B           | 3B            | No       | 0            | 157€              |
| gemma-3-4b                 | 4B           | 4B            | No       | 0            | 156€              |
| lfm2-2.6b                  | 2.6B         | 2.6B          | No       | 0            | 126€              |
| llama-3.2-3b-instruct      | 3B           | 3B            | No       | 0            | 125€              |
| granite-4.0-h-micro        | 3B           | 3B            | No       | 0            | 100€              |
| ministral-8b-2410          | 8B           | 8B            | No       | 0            | 60€               |
| qwen3-1.7b                 | 1.7B         | 1.7B          | No       | 0            | 57€               |

*median result out of five runs, often less for reasoning models due to resource limitation (one 24b run can take multiple hours). human score is the average winnings from the first 999 shows ([source](https://www.stern.de/kultur/tv/jubilaeum-von--wer-wird-millionaer---zahlen-und-fakten-aus-999-ausgaben-3605146.html)).

### Cloud

| Model Name                               | Total Params | Active Params | Million Wins | Average Winnings |
| ---------------------------------------- | ------------ | ------------- | ------------ | ---------------- |
| gpt-5 (medium)                           | N/A          | N/A           | 36           | 813.783€         |
| google/gemini-2.5-pro                    | N/A          | N/A           | 33           | 742.004€         |
| o3 (medium)                              | N/A          | N/A           | 31           | 716.546€         |
| o4-mini (medium)                         | N/A          | N/A           | 21           | 512.221€         |
| z-ai/glm-4.5-FP8                         | 355B         | 32B           | 17           | 410.813€         |
| qwen/qwen3-235b-a22b                     | 235B         | 22B           | 15           | 369.027€         |
| gpt-4o                                   | N/A          | N/A           | 12           | 302.186€         |
| gpt-5-nano (medium)                      | N/A          | N/A           | 12           | 299.494€         |
| z-ai-glm-4.5-air-FP8                     | 106B         | 12B           | 12           | 281.459€         |
| gpt-5 (minimal)                          | N/A          | N/A           | 11           | 277.661€         |
| openai/gpt-oss-120b                      | 120B         | 120B          | 11           | 275.564€         |
| gpt-4.1                                  | N/A          | N/A           | 10           | 256.073€         |
| google/gemini-2.5-flash                  | N/A          | N/A           | 7            | 205.816€         |
| qwen/qwq-32b                             | 32B          | 32B           | 8            | 197.799€         |
| qwen/qwen3-235b-a22b-2507                | 235B         | 22B           | 7            | 163.144€         |
| deepseek/deepseek-chat-v3-0324           | 67.1B        | 67.1B         | 6            | 161.492€         |
| meta-llama/llama-4-maverick              | 400B         | 18B           | 6            | 161.411€         |
| c4ai-command-a-03-2025                   | 111B         | 111B          | 6            | 155.636€         |
| deepseek/deepseek-chat-v3.1              | 68.5B        | 68.5B         | 6            | 142.581€         |
| moonshotai/kimi-k2                       | 1T           | 32B           | 4            | 125.136€         |
| gpt-4.1-mini                             | N/A          | N/A           | 3            | 113.616€         |
| qwen/qwen3-coder                         | 480B         | 480B          | 4            | 92.022€          |
| Behemoth-123B-v1.2                       | 123B         | 123B          | 3            | 84.963€          |
| gpt-4o-mini                              | N/A          | N/A           | 2            | 74.698€          |
| google/gemini-2.5-flash-lite             | N/A          | N/A           | 2            | 63.107€          |
| meta-llama/llama-3.3-70b-instruct        | 70B          | 70B           | 2            | 58.309€          |
| gpt-5-mini (minimal)                     | N/A          | N/A           | 1            | 53.618€          |
| mistralai/mistral-small-3.2-24b-instruct | 24B          | 24B           | 1            | 41.017€          |
| gpt-4.1-nano                             | N/A          | N/A           | 1            | 37.838€          |
| google/gemma-3-27b-it                    | 27B          | 27B           | 0            | 7.634€           |
| gpt-5-nano (minimal)                     | N/A          | N/A           | 0            | 2.324€           |
| microsoft/phi-4                          | 14B          | 14B           | 0            | 1.892€           |
| meta-llama/llama-3.2-1b-instruct         | 1B           | 1B            | 0            | 155€             |
| meta-llama/llama-3.2-3b-instruct         | 3B           | 3B            | 0            | 121€             |

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
