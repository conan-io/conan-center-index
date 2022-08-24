from conan import ConanFile, tools
from conans import CMake
import os


class GeotransTestConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake", "cmake_find_package_multi"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.build.cross_building(self, self):
            # NOTE: In order to use this library, the MPCCS_DATA environment variable *must* be set.
            # The path to the appropriate data directory is available in the env_info variable. This can be
            # accessed from a consumer package using `self.deps_env_info["geotrans"].MPCCS_DATA.
            # Alternatively, this data directory can be moved to a location of your choice from its location
            # in `res`, using the `imports()` method.
            # This new location can then be used as the value for the MPCCS_DATA environment variable.
            # TODO: should be automatically injected in self.run in conan v2
            with tools.environment_append(
                {"MSPCCS_DATA": self.deps_env_info["geotrans"].MPCCS_DATA}
            ):
                bin_path = os.path.join("bin", "test_package")
                self.run(bin_path, run_environment=True)
