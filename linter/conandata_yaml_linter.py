import argparse
import copy
import os
import sys
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
        pretty_print_yaml_validate_error(args, error)
        sys.exit(1)
    except BaseException as error:
        pretty_print_yaml_validate_error(args, error)
        sys.exit(1)

    exit_code = 0
    patches_path = os.path.join(os.path.dirname(args.path), "patches")
    actual_patches = []
    if os.path.isdir(patches_path):
        for root, _, files in os.walk(patches_path):
            for f in files:
                actual_patches.append(os.path.join(root[len(patches_path)+1:], f)) 
    unused_patches = copy.copy(actual_patches)
    if "patches" in parsed:
        for version in parsed["patches"]:
            patches = parsed["patches"][version]
            for i, patch in enumerate(patches):
                patch_file_name = str(patch["patch_file"])
                if not patch_file_name.startswith("patches/"):
                    print(
                        f"::error file={args.path},line={type.start_line},endline={type.end_line},"
                        f"title=conandata.yml patch path error"
                        f"::'patches' should be located in `patches` subfolder"
                    )
                    exit_code = 1
                else:
                    patch_file_name = patch_file_name[8:]
                    if patch_file_name in unused_patches:
                        unused_patches.remove(patch_file_name)
                    if patch_file_name not in actual_patches:
                        print(
                            f"::error file={args.path},line={patch['patch_file'].start_line},endline={patch['patch_file'].end_line},"
                            f"title=conandata.yml patch existence"
                            f"::The file `{patch_file_name}` does not exist in the `patches` folder"
                        )
                        exit_code = 1

                # Individual report errors for each patch object
                try:
                    parsed["patches"][version][i].revalidate(patch_fields)
                except YAMLValidationError as error:
                    pretty_print_yaml_validate_error(args, error)
                    exit_code = 1
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

                # v2 migrations suggestion
                if "base_path" in parsed["patches"][version][i]:
                    base_path = parsed["patches"][version][i]["base_path"]
                    print(
                        f"::notice file={args.path},line={base_path.start_line},endline={base_path.end_line},"
                        f"title=conandata.yml v2 migration suggestion"
                        "::'base_path' should not be required once a recipe has been upgraded to take advantage of"
                        " layouts (see https://docs.conan.io/en/latest/reference/conanfile/tools/layout.html) and"
                        " the new helper (see https://docs.conan.io/en/latest/reference/conanfile/tools/files/patches.html#conan-tools-files-apply-conandata-patches)"
                    )
    for p in unused_patches:
        print(
            f"::error file={patches_path},"
            f"title=patch file unused"
            f"::Patch file {p} is not referenced in {args.path}"
        )
        exit_code = 1

    sys.exit(exit_code)


def pretty_print_yaml_validate_error(args, error):
    snippet = error.context_mark.get_snippet().replace("\n", "%0A")
    print(
        f"::error file={args.path},line={error.context_mark.line},endline={error.problem_mark.line+1},"
        f"title=conandata.yml schema error"
        f"::Schema outlined in {CONANDATA_YAML_URL}#patches-fields is not followed.%0A%0A{error.problem} in %0A{snippet}%0A"
    )


if __name__ == "__main__":
    main()
