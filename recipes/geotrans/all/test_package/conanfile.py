import os
from conans import ConanFile, CMake, tools


class GeotransTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = (
        "cmake",
        "cmake_find_package",
    )

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self):
            # NOTE: In order to use this library, the MPCCS_DATA environment variable *must* be set.
            # The path to the appropriate data directory is available in the env_info variable. This can be
            # accessed from a consumer package using `self.deps_env_info["geotrans"].MPCCS_DATA.
            # Alternatively, this data directory can be moved to a location of your choice from its location
            # in `res`, using the `imports()` method.
            # This new location can then be used as the value for the MPCCS_DATA environment variable.
            with tools.environment_append(
                {"MSPCCS_DATA": self.deps_env_info["geotrans"].MPCCS_DATA}
            ):
                bin_path = os.path.join("bin", "example")
                self.run(bin_path, run_environment=True)
