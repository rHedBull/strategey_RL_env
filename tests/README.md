
# Code quality

### pre-commit

This project uses [pre-commit](https://pre-commit.com/) to enforce code quality.
It must be executed manually!

```bash
pre-commit run -a
```


### time profiling

```bash
python -m cProfile -o output.prof main.py
snakeviz output.prof
```

| tiles | sim_map.create_map | map_square.draw |
|-------|--------------------|-----------------|
| 10    | 0.000              | 0.000           |
| 10^2  | 0.000              | 0.000           |
| 10^3  | 0.000              | 0.000           |
| 10^4  | 0.000              | 0.000           |
| 10^5  | 0.000              | 0.000           |
| 10^6  | 23.6               | 9.08            |
| 10^9  | 0.000              | 0.000           |
### memory profiling

add the following to the functions you want to profile

```python
from memory_profiler import profile
@profile
def your_function():
    pass
```

run the script with the following command
```bash
python -m memory_profiler your_script.py
```

| memory | spike 1 | spike_2 |
|--------|---------|---------|
| 10     | 0.000   | 0.000   |
| 10^2   | 0.000   | 0.000   |
| 10^3   | 0.000   | 0.000   |
| 10^4   | 0.000   | 0.000   |
| 10^5   | 0.000   | 0.000   |
| 10^6   | 23.6    | 9.08    |
| 10^9   | 0.000   | 0.000   |
