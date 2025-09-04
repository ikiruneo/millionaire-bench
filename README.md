# "Wer wird Millionär?" LLM Benchmark

 i have created a benchmark for german "who wants to be millionaire" questions. there are 45x15 questions, all 45 rounds go from easy to hard and all tested models ran through all 45 rounds and got kicked out of a round if the answer was wrong, keeping the current winnings. no jokers.

i am a bit limited with the selection of llm's since i run them on my framework laptop 13 (amd ryzen 5 7640u with 32 gb ram), so i mainly used smaller llm's. also, qwen3's thinking went on for way to long for each question so i just tested non-thinking models except for gpt-oss-20b (low). but in my initial testing for qwen3-4b-thinking-2507, it seemed to worsen the quality of answers at least for the first questions.

the first few questions are often word-play and idioms questions needing great understanding of the german language. these proved to be very hard for most llm's but are easily solvable by the average german. once the first few questions were solved the models had an easier time answering.

i tried to use optimal model settings and included them in the table, let me know if they could be improved. all models are quant Q4_K_M.

i have close to no python coding ability so the main script was created with qwen3-coder. the project (with detailed results for each model, and the queationaire) is open souce and available on github.

## Usage

1. Make sure your LLM server (e.g., LM Studio) is running (default is `http://localhost:1234`)
2. Edit the config.json, change `model` and `inference_parameters` if needed
3. Run the benchmark script:
```bash
python3 benchmark_llm.py
```

4. When prompted, enter which question to start with:
	- Enter `0` to play all 45 rounds sequentially
	- Enter a number between `1`-`45` to play with that question set (1x15 Questions)

## Benchmark Results

### Locally by myself
| Model Name | Total Params | Active Params | Average Winnings | Million Wins | Parameters |
|------------|---------------|--------------|------------------|--------------|------------|
| qwen3-30b-a3b-2507 | 30B | 3B | 118.111€ | 5 | T:0.7, K:20, P:0.8, Min:0.0 |
| gpt-oss-20b (low) | 21B | 4B | 80.177€* | 3 | T:1, K:0, P:1.0, Min:0.0 |
| mistral-small-3.2 | 24B | 24B | 63.812€* | 2 | T:0.15, K:40, P:0.95, Min:0.05 |
| mistral-nemo-instruct-2407 | 12B | 12B | 34.383€ | 1 | T:0.3, K:-1, P:0.77, Min:0.025 |
| microsoft/phi-4 | 14B | 14B | 25.987€ | 1 | T:0.6, K:40, P:0.9, Min:0.05 |
| gemma-3-12b | 12B | 12B | 24.291€ | 1 | T:0.8, K:40, P:0.9, Min:0.05 |
| hermes-4-14b | 14B | 14B | 14.916€ | 0 | T:0.6, K:20, P:0.95, Min:0.05 |
| qwen/qwen3-4b-2507 | 4B | 4B | 948€ | 0 | T:0.7, K:40, P:0.8, Min:0.05 |
| granite-3.2-8b | 8B | 8B | 620€ | 0 | T:0.6, K:50, P:0.9, Min:0.05 |
| meta-llama-3.1-8b-instruct | 8B | 8B | 484€ | 0 | T:0.6, K:40, P:0.9, Min:0.05 |
| phi-4-mini-instruct | 3B | 3B | 157€ | 0 | T:0.8, K:40, P:0.95, Min:0.05 |
| gemma-3-4b | 4B | 4B | 156€ | 0 | T:1, K:64, P:0.95, Min:0 |
| llama-3.2-3b-instruct | 3B | 3B | 125€ | 0 | T:0.6, K:40, P:0.9, Min:0.05 |

- *indicates only one, 45 round, run
- all other winnings are the median result out of 5 runs
- `gpt-oss-20b (low)` is the only thinking model tested

### User Submitted

| Model Name | Total Params | Active Params | Average Winnings | Million Wins | Parameters |
|:-------------------------------------------|:-------------|:--------------|:-----------------|:-------------|:----------------------------|
| gpt-5 (medium) | N/A | N/A | 813.783€ | 36 | T:0.6, P:1 |
| google/gemini-2.5-pro | N/A | N/A | 742.004€ | 33 | T:0.6, P:1 |
| o3 (medium) | N/A | N/A | 716.546€ | 31 | T:0.6, P:1 |
| o4-mini (medium) | N/A | N/A | 512.221€ | 21 | T:0.6, P:1 |
| z-ai/glm-4.5-FP8 | 355B | 32B | 410.813€ | 17 | T:0.6, K:40, P:0.9, Min:0.1 |
| qwen/qwen3-235b-a22b | 235B | 22B | 369.027€ | 15 | T:0.6, P:1 |
| gpt-4o | N/A | N/A | 302.186€ | 12 | T:0.6, P:1 |
| gpt-5-nano (medium) | N/A | N/A | 299.494€ | 12 | T:0.6, P:1 |
| z-ai-glm-4.5-air-FP8 | 106B | 12B | 281.459€ | 12 | T:0.6, K:40, P:0.9, Min:0.1 |
| gpt-5 (minimal) | N/A | N/A | 277.661€ | 11 | T:0.6, P:1 |
| openai/gpt-oss-120b | 120B | 120B | 275.564€ | 11 | T:0.6, P:1 |
| gpt-4.1 | N/A | N/A | 256.073€ | 10 | T:0.6, P:1 |
| google/gemini-2.5-flash | N/A | N/A | 205.816€ | 7 | T:0.6, P:1 |
| qwen/qwq-32b | 32B | 32B | 197.799€ | 8 | T:0.6, P:1 |
| qwen/qwen3-235b-a22b-2507 | 235B | 22B | 163.144€ | 7 | T:0.6, P:1 |
| deepseek/deepseek-chat-v3-0324 | 67.1B | 67.1B | 161.492€ | 6 | T:0.6, P:1 |
| meta-llama/llama-4-maverick | 400B | 18B | 161.411€ | 6 | T:0.6, P:1 |
| c4ai-command-a-03-2025 | 111B | 111B | 155.636€ | 6 | T:0.6, K:40, P:0.9, Min:0.1 |
| deepseek/deepseek-chat-v3.1 | 68.5B | 68.5B | 142.581€ | 6 | T:0.6, P:1 |
| moonshotai/kimi-k2 | 1T | 32B | 125.136€ | 4 | T:0.6, P:1 |
| gpt-4.1-mini | N/A | N/A | 113.616€ | 3 | T:0.6, P:1 |
| qwen/qwen3-coder | 480B | 480B | 92.022€ | 4 | T:0.6, P:1 |
| Behemoth-123B-v1.2 | 123B | 123B | 84.963€ | 3 | T:0.6, K:40, P:0.9, Min:0.1 |
| gpt-4o-mini | N/A | N/A | 74.698€ | 2 | T:0.6, P:1 |
| google/gemini-2.5-flash-lite | N/A | N/A | 63.107€ | 2 | T:0.6, P:1 |
| meta-llama/llama-3.3-70b-instruct | 70B | 70B | 58.309€ | 2 | T:0.6, P:1 |
| gpt-5-mini (minimal) | N/A | N/A | 53.618€ | 1 | T:0.6, P:1 |
| mistralai/mistral-small-3.2-24b-instruct | 24B | 24B | 41.017€ | 1 | T:0.6, P:1 |
| gpt-4.1-nano | N/A | N/A | 37.838€ | 1 | T:0.6, P:1 |
| google/gemma-3-27b-it | 27B | 27B | 7.634€ | 0 | T:0.6, P:1 |
| gpt-5-nano (minimal) | N/A | N/A | 2.324€ | 0 | T:0.6, P:1 |
| microsoft/phi-4 | 14B | 14B | 1.892€ | 0 | T:0.6, P:1 |
| meta-llama/llama-3.2-1b-instruct | 1B | 1B | 155€ | 0 | T:0.6, P:1 |
| meta-llama/llama-3.2-3b-instruct | 3B | 3B | 121€ | 0 | T:0.6, P:1 |

thanks to the reddit users `FullOf_Bad_Ideas` and `Pauli1_Go` for their help.

### Different quant tests
| Model Name | Q4_K_M | Q8_0 | Difference |
|------------|--------|------|------------|
| qwen3-4b-instruct-2507 | 643€ | 4.457€ | +593% |
| gemma-3-4b | 103€ | 141€ | +36% |
| llama-3.2-3b-instruct | 104€ | 78€ | -25% |

ran every test 3 times and picked the median. results are very inconsistent for small models (±50%)

## Rules
- 45 unique rounds
- if lost, current winnings are kept
- no jokers

## Resources
Questions: https://github.com/GerritKainz/wer_wird_millionaer
