from time import perf_counter_ns

def fmt_ns(time_ns: int):
    scales = {
        "ns": 1e0,
        "us": 1e3,
        "ms": 1e6,
        "s": 1e9,
    }

    for name, size in scales.items():
        if time_ns < size * 1e3:
            return f"{time_ns/size:.2f}{name}"

    time_s = time_ns // 10**9
    if time_s / 60 / 60 / 24 > 1:
        return f"{int(time_s/60/60/24)} days"
    elif time_s / 60 / 60 > 1:
        return f"{int(time_s/60/60):2d}:{int(time_s//60)%60:2d} hh:mm"
    elif time_s / 60 > 1:
        return f"{time_s//60:2d}:{time_s%60:2d} mm:ss"


def timer(func):
    def wrapper(*args, **kwargs):
        start_ns = perf_counter_ns()
        res = func(*args, **kwargs)
        time_ns = perf_counter_ns() - start_ns
        print(f"{func.__name__} took {fmt_ns(time_ns)}")
        return res

    return wrapper
