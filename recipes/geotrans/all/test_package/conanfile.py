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
            with tools.environment_append(
                {"MSPCCS_DATA": self.deps_user_info["geotrans"].data_path}
            ):
                bin_path = os.path.join("bin", "example")
                self.run(bin_path, run_environment=True)
