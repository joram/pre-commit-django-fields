import argparse
from typing import List


def print_arguments(filenames: List[str]):
    for filename in filenames:
        filename = "./"+filename.replace(".py", "")
        i = __import__(filename)
        print(dir(i))

    # suggest `id = CustomShortUUID(.....)` in the output
    # try and make it generic, algorithm based instead of a hardcoded list.


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("filenames", nargs="*")
    args = parser.parse_args()

    print_arguments(args.filenames)


if __name__ == "__main__":
    main()
