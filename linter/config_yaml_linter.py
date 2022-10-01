from strictyaml import load, Map, Str, YAMLValidationError, MapPattern
import argparse


def file_path(a_string):
    from os.path import isfile
    if not isfile(a_string):
        raise argparse.ArgumentTypeError(f"{a_string} does not point to a file")
    return a_string

def main():
    parser = argparse.ArgumentParser(description="Validate yaml file.")
    parser.add_argument(
        "path",
        nargs="?",
        type=file_path,
        help="file to validate.",
    )
    args = parser.parse_args()

    schema = Map(
        {"versions": MapPattern(Str(), Map({"folder": Str()}), minimum_keys=1)}
    )

    with open(args.path) as f:
        content = f.read()

    try:
        load(content, schema)
    except YAMLValidationError as error:
        e = error.__str__().replace("\n", "%0A")
        print(
            f"::error file={args.path},line={error.context_mark.line},endline={error.problem_mark.line},"
            f"title=config.yml schema error"
            f"::{e}\n"
        )
        exit(1)

if __name__ == "__main__":
    main()
