import yaml
from pathlib import Path
from subprocess import run
from argparse import ArgumentParser


def recipe_config(recipes):
    for recipe, data in recipes.items():
        config_file = Path("recipes") / recipe / "config.yml"
        with open(config_file, "r") as fp:
            config = yaml.safe_load(fp)
            for version in data["versions"]:
                available_versions = config["versions"]
                if version not in available_versions:
                    raise KeyError(f"Version '{version}' for '{recipe}' not in available versions")
                folder = config["versions"][version]["folder"]
                yield { "recipe": recipe, "version": version, "folder": folder}


def affected_recipes(changeset):
    for change in changeset.split():
        elements = Path(change).parts
        if elements[0] == "recipes":
            yield elements[1]


def load_packages() -> dict:
    with open("entos-packages.yml", 'r') as fp:
        return yaml.safe_load(fp)


def main():
    parser = ArgumentParser(description="package tools for the entos conan repository")
    parser.add_argument("--export", help="export all packages to the local cache", action="store_true")
    parser.add_argument("--build", help="build the packages affected by the given change set")
    args = parser.parse_args()

    configs = list(recipe_config(load_packages()))
    if args.export:
        for config in configs:
            cmd = "conan export recipes/{recipe}/{folder} --version={version}".format(**config)
            run(cmd.split(), check=True)
        return

    if args.build:
        recipes = set(affected_recipes(args.build))
        if len(recipes) > 1:
            raise RuntimeError("PR contains a change to more than one recipe")
        if len(recipes) == 0:
            print("No changed recipes")
            return

        recipe = recipes.pop()
        recipes_to_build = [config for config in configs if config["recipe"] == recipe]
        if len(recipes_to_build) == 0:
            raise RuntimeError(f"updated recipe '{recipe}' is not in the entos package list")

        for recipe_to_build in recipes_to_build:
            cmd = "conan create recipes/{recipe}/{folder} --version={version} --build=missing".format(**recipe_to_build)
            cmd += " -c tools.system.package_manager:mode=install"
            run(cmd.split(), check=True)


if __name__ == "__main__":
    try:
        main()
    except Exception as err:
        print(f"::error ::{err}")
        exit(1)
