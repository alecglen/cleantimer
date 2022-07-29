# cleantimer
Track progress of long-running scripts, without cluttering your code with log statements.

cleantimer is a minimal wrapper around a couple of my favorite packages for timing scripts - [contexttimer](https://pypi.org/project/contexttimer/) and [tqdm](https://pypi.org/project/tqdm/). It merges their most useful features in a clean API based simply on the way I've found I like to use them. Hopefully you find it simply useful. 😊

## Installation

```pip install cleantimer```



## Usage

Import:

```from cleantimer import CTimer```

| Use case | Code | Output |
| -------- | ---- | ------ |
| A basic timer with a message for what you're timing | <code>with CTimer("Waking up"):<br>&nbsp;&nbsp;&nbsp;&nbsp;sleep(4)</code> | <code>Waking up...done. (4.0s)</code> |
| Print with varying precision | <code>with CTimer("Waking up", 3):<br>&nbsp;&nbsp;&nbsp;&nbsp;sleep(4.123456)</code> | <code>Waking up...done. (4.123s)</code> |
| Sub-timers | <code>with CTimer("Making breakfast") as timer:<br>&nbsp;&nbsp;&nbsp;&nbsp;sleep(2)<br>&nbsp;&nbsp;&nbsp;&nbsp;with timer.child("cooking eggs") as eggtimer:<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;sleep(3)<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;with timer.child("pouring juice"):<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;sleep(1)</code> | <code>Making breakfast...<br>&nbsp;&nbsp;&nbsp;&nbsp;cooking eggs...done. (3.0s)<br>&nbsp;&nbsp;&nbsp;&nbsp;pouring juice...done. (1.0s)<br>done. (6.0s)` |
| Progress meter on a Pandas apply | <code>df = pd.DataFrame({"A": list(range(10000))})<br>def times2(row): return row["A"] * 2<br><br>with CTimer("Computing doubles") as timer:<br>&nbsp;&nbsp;&nbsp;&nbsp;df["2A"] = timer.progress_apply(df, times2)</code> | <code>Computing doubles...<br>&nbsp;&nbsp;&nbsp;&nbsp;: 100% ██████████████████████████ 10000/10000 [00:07<00:00, 135869.18it/s]<br>done. (7.4s)</code> |
| Grouped apply | <code>df = pd.DataFrame({"A": list(range(10000))})<br>def times2(row): return row["A"] * 2<br><br>with CTimer("Computing doubles") as timer:<br>&nbsp;&nbsp;&nbsp;&nbsp;df["2A"] = timer.progress_apply(df, times2)</code> | <code>Computing doubles...<br>&nbsp;&nbsp;&nbsp;&nbsp;: 100% ██████████████████████████ 10000/10000 [00:07<00:00, 135869.18it/s]<br>done. (7.4s)</code> |