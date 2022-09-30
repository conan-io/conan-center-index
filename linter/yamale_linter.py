from strictyaml import load, Map, Str, Int, Seq, YAMLValidationError, MapPattern
import argparse


def main():
    parser = argparse.ArgumentParser(description="Validate yaml files.")
    parser.add_argument(
        "path",
        metavar="PATH",
        default="./",
        nargs="?",
        help="folder to validate. Default is current directory.",
    )
    parser.add_argument(
        "-s",
        "--schema",
        default="schema.yaml",
        help="filename of schema. Default is schema.yaml.",
    )
    args = parser.parse_args()

    schema = Map(
        {"versions": MapPattern(Str(), Map({"folder": Str()}), minimum_keys=1)}
    )

    try:
        with open(args.path) as f:
            person = load(f.read(), schema)
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
