# "Wer wird Millionär?" LLM Benchmark

A benchmark using questions from the German version of "Who Wants to Be a Millionaire?". It consists of 45 games, each with 15 questions of increasing difficulty. All tested models played through the 45 games at least once. Each game is ended with the first incorrect answer, and the winnings at that point are recorded. No jokers were used.

The initial questions often involve wordplay and idioms, requiring a deep understanding of the German language. These proved challenging for most LLMs, though they are easily solvable by the average German. Once past these early hurdles, the models generally found the subsequent questions easier to answer.

My selection of LLMs is limited as I ran them on my Framework Laptop 13 (AMD Ryzen 5 7640U with 32 GB of RAM), which necessitated the use of smaller models. All models were Q4_K_M quantized and, if available, recommended settings were used.

## Quick Start

`Benchmark.py` should work with local LLM servers like LM Studio as well as any other OpenAI API compatible URL like openrouter.ai/api.

1. Edit the benchmark.py: change `SERVER_URL`, add `API_KEY` (if needed), set `MODEL_NAME` and sampling parameters.

2. Run the benchmark script:
   
   ```
   python3 benchmark.py
   ```

3. You can view the leaderboard locally in your browser at [http://127.0.0.1:8020/](http://127.0.0.1:8020/) by running this in your `millionaire-bench` folder:
   
   ```
   python3 -m http.server 8020
   ```

Check the [/wiki/guide](https://github.com/ikiruneo/millionaire-bench/wiki/guide) for more detailed instructions. 

## Benchmark Results (Local & Cloud)

https://millionaire-bench.referi.de/

[![Leaderboard Preview](http://github.com/ikiruneo/millionaire-bench/blob/main/leaderboard/preview.png?raw=true "Leaderboard Preview")](https://millionaire-bench.referi.de/)

Human average winnings of the first 999 shows is 36 000€ ([source](https://www.stern.de/kultur/tv/jubilaeum-von--wer-wird-millionaer---zahlen-und-fakten-aus-999-ausgaben-3605146.html)). 

Thanks to the reddit users `FullOf_Bad_Ideas` and `Pauli1_Go` for benchmarking cloud models.

Origin of the Q&A's: 
[https://github.com/GerritKainz/wer_wird_millionaer]()
