# cleantimer

Track progress of long-running scripts, without cluttering your code with log statements.

cleantimer is a minimal wrapper around a couple of my favorite packages for timing scripts - [contexttimer](https://pypi.org/project/contexttimer/) and [tqdm](https://pypi.org/project/tqdm/). It merges their most useful features in a clean API based simply on the way I've found I like to use them. Hopefully you find it simply useful. 😊

## Installation

`pip install cleantimer`

### Import:

`from cleantimer import CTimer`

## Use cases

### A basic timer with a message for what you're timing:

```Python
with CTimer("Waking up"):
    sleep(4)
```

```
Waking up (3:22PM)...done. (4.0s)
```

### Print with varying precision:

```Python
with CTimer("Waking up", 3):
    sleep(4.123456)
```

```
Waking up (3:22PM)...done. (4.123s)
```

### Sub-timers

```Python
with CTimer("Making breakfast") as timer:
    sleep(2)
    with timer.child("cooking eggs") as eggtimer:
        sleep(3)
    with timer.child("pouring juice"):
        sleep(1)
```

```
Making breakfast (3:22PM)...
    cooking eggs (3:22PM)...done. (3.0s)
    pouring juice (3:23PM)...done. (1.0s)
done. (6.0s)
```

### Progress meter on a Pandas apply

```Python
df = pd.DataFrame({"A": list(range(10000))})
def times2(row): return row["A"] * 2

with CTimer("Computing doubles") as timer:
    df["2A"] = timer.progress_apply(df, times2)
```

```
Computing doubles (3:22PM)...
    : 100% ██████████████████████████ 10000/10000 [00:07<00:00, 135869it/s]
done. (7.4s)
```

### Segmented progress meter

```Python
df = pd.DataFrame({"A": list(range(10000)), "type": [1]*5000 + [2]*5000})
def times2(row): return row["A"] * 2

with CTimer("Computing doubles") as timer:
    df["2A"] = timer.progress_apply(df, times2, split_col="type", message="part {}")
```

```
Computing doubles (3:22PM)...
    part 1: 100% ██████████████████████████ 5000/5000 [00:07<00:00, 135869it/s]
    part 2: 100% ██████████████████████████ 5000/5000 [00:07<00:00, 122854it/s]
done. (8.2s)
```
