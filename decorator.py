def cache_args(func):
    __cache = {}
    def calc_value(arg):
        return __cache[arg] = func(arg) if arg not in __cache else __cache[arg]
    return calc_value


@cache_args
def long_heavy(num):
    print(f"Долго и сложно {num}")
    return num**num

print(long_heavy(1))
print(long_heavy(1))
print(long_heavy(2))
print(long_heavy(2))