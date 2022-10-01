from strictyaml import (
    load,
    Map,
    Str,
    YAMLValidationError,
    MapPattern,
    Optional,
    Seq,
    Enum,
    Any,
)
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

    # Generic "source" objects
    sources_with_mirrors = Map({"url": Str() | Seq(Str()), "sha256": Str()})
    # sources_with_multiple_assets = MapPattern(Str(), Map({"url": Str(), "sha256": Str()}), minimum_keys=1)
    sources_with_multiple_assets = Seq(Map({"url": Str(), "sha256": Str()}))
    source_object = sources_with_mirrors | sources_with_multiple_assets

    # Platform specific archives
    known_os = ["Windows", "Linux", "Macos"]
    platform_specific_source_fields = MapPattern(
        Enum(known_os),
        MapPattern(Enum(["x86_64", "armv7", "armv8"]), source_object),
    )
    patch_fields = Map(
        {
            "patch_file": Str(),

            # Not yet wide spread
            "patch_description": Str(),
            "patch_type": Enum(["official", "conan", "portability", "backport"]),  # "vulnerability"
            Optional("patch_source"): Str(),

            # No longer required for v2 recipes?
            Optional("base_path"): Str(),
        }
    )
    outer_schema = Map(
        {
            "sources": MapPattern(Str(), Any(), minimum_keys=1),
            Optional("patches"): MapPattern(Str(), Seq(patch_fields), minimum_keys=1),
        }
    )

    with open(args.path) as f:
        content = f.read()

    try:
        parsed = load(content, outer_schema)
        print("passed outter validation\n")
        if any(os in content for os in known_os):
            print("running platform check\n")
            parsed["sources"].revalidate(
                MapPattern(Str(), platform_specific_source_fields, minimum_keys=1)
            )
        else:
            parsed["sources"].revalidate(
                MapPattern(Str(), source_object, minimum_keys=1)
            )
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
