# "Wer wird Millionär?" LLM Benchmark

A benchmark using questions from the German version of "Who Wants to Be a Millionaire?". It consists of 45 games, each with 15 questions of increasing difficulty. All tested models played through the 45 games at least once. Each game is ended with the first incorrect answer, and the winnings at that point are recorded. No jokers were used.

The initial questions often involve wordplay and idioms, requiring a deep understanding of the German language. These proved challenging for most LLMs, though they are easily solvable by the average German. Once past these early hurdles, the models generally found the subsequent questions easier to answer.

My selection of LLMs is limited as I ran them on my Framework Laptop 13 (AMD Ryzen 5 7640U with 32 GB of RAM), which necessitated the use of smaller models. All models were Q4_K_M quantized and, if available, recommended settings were used.
## Usage

1. The benchmark.py should work with local LLM servers like LM Studio and any other OpenAI API compatible URL.

2. Edit the benchmark.json, change `SERVER_URL`, add `API_KEY` (if needed), set `MODEL_NAME` and sampling parameters.

3. Run the benchmark script:
   
   ```bash
   python3 benchmark.py
   ```

Note: `benchmark_2.py` offers a more advanced implementation that goes right over my head, written by people more knowledgeable than I am. From what I understand, it's better suited for cloud-based URLs and offers concurrency and safer answer parsing.

## Benchmark Results

### Local
https://millionaire-bench.referi.de/

| Model Name             | Total | Active | Thinking | Wins |  Median |
| :--------------------- | ----: | -----: | -------: | ---: | ------: |
| mistral-small-3.2      |  24 B |   24 B |       No |    2 | 9 694 € |
| qwen3-30b-a3b-2507     |  30 B |    3 B |       No |    5 | 9 000 € |
| gemma-3-27b            |  27 B |   27 B |       No |    0 | 1 256 € |
| gpt-oss-20b-low        |  21 B |    4 B |      Yes |    3 | 1 256 € |
| phi-4                  |  14 B |   14 B |       No |    1 | 1 239 € |
| hermes-4-14b           |  14 B |   14 B |       No |    0 |   896 € |
| gemma-3-12b            |  12 B |   12 B |       No |    1 |   823 € |
| qwen3-4b-thinking-2507 |   4 B |    4 B |      Yes |    1 |   499 € |
| mistral-nemo-2407      |  12 B |   12 B |       No |    1 |   436 € |
| granite-3.2-8b         |   8 B |    8 B |       No |    0 |   204 € |
| granite-4.0-h-small    |  32 B |    9 B |       No |    0 |   177 € |
| apertus:8b             |   8 B |    8 B |       No |    0 |   167 € |
| llama-3.1-8b-instruct  |   8 B |    8 B |       No |    0 |   137 € |
| gemma-3n-e4b           |   8 B |    4 B |       No |    0 |   121 € |
| lfm2:8b-a1b            |   8 B |  1.5 B |       No |    0 |    90 € |
| lfm2-2.6b              | 2.6 B |  2.6 B |       No |    0 |    87 € |
| qwen3-4b-2507          |   4 B |    4 B |       No |    0 |    86 € |
| qwen3-1.7b-thinking    | 1.7 B |  1.7 B |      Yes |    0 |    71 € |
| granite-4-h-tiny       |   7 B |    1 B |       No |    0 |    66 € |
| gemma-3-4b             |   4 B |    4 B |       No |    0 |    53 € |
| nemotron-nano-9b-v2    |   9 B |    9 B |       No |    0 |    53 € |
| ai21-jamba-3b          |   3 B |    3 B |      Yes |    0 |    47 € |
| phi-4-mini-instruct    |   3 B |    3 B |       No |    0 |    41 € |
| granite-4.0-h-micro    |   3 B |    3 B |       No |    0 |    36 € |
| llama-3.2-3b-instruct  |   3 B |    3 B |       No |    0 |    33 € |
| qwen3-1.7b             | 1.7 B |  1.7 B |       No |    0 |    31 € |
| ministral-8b-2410      |   8 B |    8 B |       No |    0 |    20 € |
A model's Median Score is calculated from the average winnings of a test run, after discarding the top 5 and bottom 5 outlier rounds. The final score shown is the median (middle value) of all test runs for that model. For models tested multiple times, the range between their best and worst scores is also shown to indicate performance consistency. Human average winnings of the first 999 shows is 36 000€ ([source](https://www.stern.de/kultur/tv/jubilaeum-von--wer-wird-millionaer---zahlen-und-fakten-aus-999-ausgaben-3605146.html)).

### Cloud

| Model Name             |  Total | Active | Wins |    Median |
| :--------------------- | -----: | -----: | ---: | --------: |
| gpt-5 (medium)         |    N/A |    N/A |   36 | 902 743 € |
| gemini-2.5-pro         |    N/A |    N/A |   33 | 810 429 € |
| o3 (medium)            |    N/A |    N/A |   31 | 778 400 € |
| gpt-5-mini (medium)    |    N/A |    N/A |   31 | 723 491 € |
| o4-mini (medium)       |    N/A |    N/A |   21 | 515 706 € |
| glm-4.5-FP8            |  355 B |   32 B |   17 | 385 330 € |
| qwen3-235b-a22b        |  235 B |   22 B |   15 | 331 600 € |
| gpt-4o                 |    N/A |    N/A |   12 | 245 663 € |
| gpt-5-nano (medium)    |    N/A |    N/A |   12 | 242 207 € |
| glm-4.5-air-FP8        |    N/A |    N/A |    0 | 219 019 € |
| gpt-5-nano (minimal)   |    N/A |    N/A |   11 | 214 133 € |
| gpt-oss-120b           |  120 B |  120 B |   11 | 211 440 € |
| gpt-4.1                |    N/A |    N/A |   10 | 186 376 € |
| gemini-2.5-flash       |    N/A |    N/A |    7 | 121 760 € |
| qwq-32b                |   32 B |   32 B |    8 | 111 456 € |
| qwen3-235b-a22b-2507   |  235 B |   22 B |    7 |  66 899 € |
| deepseek-chat-v3-0324  | 67.1 B | 67.1 B |    6 |  64 774 € |
| llama-4-maverick       |  400 B |   18 B |    6 |  64 671 € |
| c4ai-command-a-03-2025 |  111 B |  111 B |    6 |  57 243 € |
| deepseek-chat-v3.1     | 68.5 B | 68.5 B |    6 |  40 461 € |
| kimi-k2                |    1 T |   32 B |    4 |  32 316 € |
| gpt-4.1-mini           |    N/A |    N/A |    3 |  31 789 € |
| gpt-4o-mini            |    N/A |    N/A |    2 |   8 497 € |
| gpt-5-mini (minimal)   |    N/A |    N/A |    1 |   8 137 € |
| Behemoth-123B-v1.2     |    N/A |    N/A |    3 |   5 667 € |
| gemini-2.5-flash-lite  |    N/A |    N/A |    2 |   4 307 € |
| mistral-small-3.2-24b  |   24 B |   24 B |    1 |   2 650 € |
| qwen3-coder            |  480 B |  480 B |    4 |   2 200 € |
| gpt-4.1-nano           |    N/A |    N/A |    1 |   1 677 € |
| llama-3.3-70b-instruct |   70 B |   70 B |    2 |   1 254 € |
| gemma-3-27b-it         |   27 B |   27 B |    0 |   1 216 € |
| gpt-5-nano (minimal)   |    N/A |    N/A |    0 |     303 € |
| phi-4                  |   14 B |   14 B |    0 |     204 € |
| llama-3.2-3b-instruct  |    3 B |    3 B |    0 |      50 € |
| llama-3.2-1b-instruct  |    1 B |    1 B |    0 |      34 € |
One run only. Thanks to the reddit users `FullOf_Bad_Ideas` and `Pauli1_Go` for their help.

## Resources

Questions: https://github.com/GerritKainz/wer_wird_millionaer
