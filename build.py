from os import environ
from sys import platform
from cpt.packager import ConanMultiPackager
from cpt.tools import get_bool_from_env


if __name__ == "__main__":
    environ["CONAN_USERNAME"] = "_"
    environ["CONAN_CHANNEL"] = "ci"

    is_pure_c = get_bool_from_env('IS_PURE_C')
    builder = ConanMultiPackager(
        login_username="trassir-ci-bot",
        upload="https://api.bintray.com/conan/trassir/conan-public",
        upload_only_when_stable=1,
        stable_branch_pattern="master",
        stable_channel="_",
        remotes="https://api.bintray.com/conan/trassir/conan-public"
    )
    builder.add_common_builds(pure_c=is_pure_c)
    builder.run()

# rebuild everything
