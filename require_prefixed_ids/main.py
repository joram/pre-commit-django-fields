import argparse
from django.apps import apps
from typing import List


def get_django_models(filenames: List[str]):
    print(apps.all_models.keys())
    for app_name in apps.all_models.keys():
        for model in apps.get_app_config(app_name).get_models():
            yield model


def verify_ids_are_prefixed(filenames: List[str]):
    models = get_django_models(filenames)
    print(list(models))
    # suggest `id = CustomShortUUID(.....)` in the output
    # try and make it generic, algorithm based instead of a hardcoded list.


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("filenames", nargs="*")
    args = parser.parse_args()

    verify_ids_are_prefixed(args.filenames)


if __name__ == "__main__":
    main()
