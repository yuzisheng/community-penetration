import math


def sigmod(x: float) -> float:
    return 1 / (1 + pow(math.e, -x))


def is_no_dup_elems(my_list: list) -> bool:
    return len(set(my_list)) == len(my_list)


if __name__ == '__main__':
    print(sigmod(0))
    print(is_no_dup_elems([1, 2, 1]))
    print("ok")
