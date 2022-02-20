"""
Name - Simar Singh
Email - hfv6838@wmich.edu

"""

import binascii
import math
import re
import argparse
from operator import attrgetter, itemgetter


def to_binary(address):
    return str(bin(int(address, 16)))[2:].zfill(64)


def init_list_of_objects(size, E):
    list_of_objects = list()
    for i in range(0, size):
        cache_sets = []
        for j in range(0, E):
            cache_sets.append({'valid': 0})  # different object reference each time
        list_of_objects.append(cache_sets)
    return list_of_objects


def cache_simulator():
    parser = argparse.ArgumentParser()

    # [-hv] -s <s> -E <E> -b <b> -t <tracefile>
    parser.add_argument("-v", "--full_info", dest="full_info", help="Displays full line by line trace",
                        action='store_true')
    parser.add_argument("-s", "--set_bits", dest="set_bits", help="Number of set index bits", type=int)
    parser.add_argument("-E", "--line", dest="line", help="number of lines", type=int)
    parser.add_argument("-b", "--block_bits", dest="block_bits",
                        help="Number of block bits (B = 2 b is the block size)", type=int)
    parser.add_argument("-t", "--tracefile", dest="tracefile", help="Name of the valgrind trace to replay")

    args = parser.parse_args()
    file1 = args.tracefile
    b = args.block_bits
    B = pow(2, b)
    s = args.set_bits
    E = args.line
    sets = pow(2, s)
    hits = 0
    miss = 0
    miss_eviction = 0
    index = 0

    def run_cache(address, cache):
        nonlocal index
        nonlocal hits
        nonlocal miss
        nonlocal miss_eviction
        binary_address = to_binary(address)
        t = len(binary_address) - len(str(b)) - len(str(s))
        tag_bits = len(binary_address[:len(binary_address) - b - s])
        tag = binary_address[:len(binary_address) - b - s]

        data = {'index': index, 'valid': 1, 'tag': tag,
                'block': binary_address[-b:]}
        set_location = int(binary_address[-s - b:-b], 2)

        def is_cache_full():
            is_full_bool = True
            for items in cache[set_location]:
                for key, value in items.items():
                    if key == "valid":
                        if value == 1:
                            pass
                        else:
                            is_full_bool = False
                            return is_full_bool
            return is_full_bool

        has_hit = False
        for i in cache[set_location]:
            existing_data = i
            if existing_data['valid'] == 1 and existing_data['tag'] == data['tag']:
                if args.full_info:
                    print("hit ", end='')
                hits += 1
                has_hit = True
                break

        if has_hit:
            pass
        elif not is_cache_full():
            if args.full_info:
                print("miss ", end='')
            miss += 1
            cache[set_location].remove(min(cache[set_location], key=itemgetter("valid")))
            cache[set_location].append(data)

        else:
            if args.full_info:
                print("miss eviction ", end='')
            miss += 1
            cache[set_location].remove(min(cache[set_location],
                                           key=lambda x: x["index"] if x["valid"] else -1))
            cache[set_location].append(data)
            miss_eviction += 1

        index += 1

    with open(file1) as f:
        lines = f.readlines()
        length_of_list = len(lines) + 1
        cache = init_list_of_objects(length_of_list, E)

        for line in lines:
            if line == " ":
                break
            line.strip()
            line = line.replace("\n", "")
            split_line = line[3:].split(",", 2)
            address = split_line[0]
            if line[0] == 'I':
                pass
            else:
                if args.full_info:
                    print("{} ".format(line.lstrip().rstrip()), end='', flush=True)

            if line[1] == 'L' or line[1] == 'S':
                run_cache(address, cache)

            elif line[1] == 'M':
                run_cache(address, cache)
                run_cache(address, cache)
            index += 1

            if args.full_info and not line[0] == 'I':
                print("")

        print("hits:", hits, "misses:", miss, "evictions", miss_eviction)


if __name__ == '__main__':
    cache_simulator()
