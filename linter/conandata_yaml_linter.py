import argparse
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
from yaml_linting import file_path


CONANDATA_YAML_URL = "https://github.com/conan-io/conan-center-index/blob/master/docs/adding_packages/conandata_yml_format.md"


def main():
    parser = argparse.ArgumentParser(
        description="Validate Conan's 'conandata.yaml' file to ConanCenterIndex's requirements."
    )
    parser.add_argument(
        "path",
        nargs="?",
        type=file_path,
        help="file to validate.",
    )
    args = parser.parse_args()

    patch_fields = Map(
        {
            "patch_file": Str(),
            "patch_description": Str(),
            "patch_type": Enum(
                ["official", "conan", "portability", "bugfix", "vulnerability"]
            ),
            Optional("patch_source"): Str(),
            # No longer required for v2 recipes with layouts
            Optional("base_path"): Str(),
        }
    )
    schema = Map(
        {
            "sources": MapPattern(Str(), Any(), minimum_keys=1),
            Optional("patches"): MapPattern(Str(), Seq(Any()), minimum_keys=1),
        }
    )

    with open(args.path, encoding="utf-8") as f:
        content = f.read()

    try:
        parsed = load(content, schema)
    except YAMLValidationError as error:
        pretty_print_yaml_validate_error(args, error) # Error when "source" is missing or when "patches" has no versions
        return
    except BaseException as error:
        pretty_print_yaml_validate_error(args, error) # YAML could not be parsed
        return

    if "patches" in parsed:
        for version in parsed["patches"]:
            patches = parsed["patches"][version]
            if version not in parsed["sources"]:
                print(
                    f"::warning file={args.path},line={patches.start_line},endline={patches.end_line},"
                    f"title=conandata.yml inconsistency"
                    f"::Patch(es) are listed for version `{version}`, but there is source for this version."
                    f" You should either remove `{version}` from the `patches` section, or add it to the"
                    f" `sources` section"
                )
            for i, patch in enumerate(patches):
                # Individual report errors for each patch object
                try:
                    parsed["patches"][version][i].revalidate(patch_fields)
                except YAMLValidationError as error:
                    pretty_print_yaml_validate_warning(args, error) # Warning when patch fields are not followed
                    continue

                # Make sure `patch_source` exists where it's encouraged
                type = parsed["patches"][version][i]["patch_type"]
                if (
                    type in ["official", "bugfix", "vulnerability"]
                    and not "patch_source" in patch
                ):
                    print(
                        f"::warning file={args.path},line={type.start_line},endline={type.end_line},"
                        f"title=conandata.yml schema warning"
                        f"::'patch_type' should have 'patch_source' as per {CONANDATA_YAML_URL}#patch_type"
                        " it is expected to have a source (e.g. a URL) to where it originates from to help with"
                        " reviewing and consumers to evaluate patches"
                    )


def pretty_print_yaml_validate_error(args, error):
    snippet = error.context_mark.get_snippet().replace("\n", "%0A")
    print(
        f"::error file={args.path},line={error.context_mark.line},endline={error.problem_mark.line+1},"
        f"title=conandata.yml schema error"
        f"::Schema outlined in {CONANDATA_YAML_URL}#patches-fields is not followed.%0A%0A{error.problem} in %0A{snippet}%0A"
    )
    
def pretty_print_yaml_validate_warning(args, error):
    snippet = error.context_mark.get_snippet().replace("\n", "%0A")
    print(
        f"::warning file={args.path},line={error.context_mark.line},endline={error.problem_mark.line+1},"
        f"title=conandata.yml schema warning"
        f"::Schema outlined in {CONANDATA_YAML_URL}#patches-fields is not followed.%0A%0A{error.problem} in %0A{snippet}%0A"
    )


if __name__ == "__main__":
    main()
