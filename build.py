from os import environ
from sys import platform
from cpt.packager import ConanMultiPackager
from cpt.tools import get_bool_from_env


if __name__ == "__main__":
    environ["CONAN_USERNAME"] = "_"
    environ["CONAN_CHANNEL"] = "ci"
    if "CONAN_OPTIONS" in environ and environ["CONAN_OPTIONS"] != "":
        environ = "*:shared=True," + environ["CONAN_OPTIONS"]
    else:
        environ["CONAN_OPTIONS"] = "*:shared=True"

    conan_config_url = None
    if platform != "linux":
        conan_config_url="https://github.com/trassir/conan-config.git"

    is_pure_c = get_bool_from_env('IS_PURE_C')
    builder = ConanMultiPackager(
        login_username="trassir-ci-bot",
        upload=("https://api.bintray.com/conan/trassir/conan-public", True, "bintray-trassir"),
        upload_only_when_stable=1,
        stable_branch_pattern="master",
        stable_channel="_",
        config_url=conan_config_url,
        remotes="https://api.bintray.com/conan/trassir/conan-public"
    )
    builder.add_common_builds(pure_c=is_pure_c)
    builder.run()

# rebuild everything 2
