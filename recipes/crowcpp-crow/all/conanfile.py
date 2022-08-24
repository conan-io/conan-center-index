from conan import ConanFile, tools
from conans import CMake
import os

required_conan_version = ">=1.33.0"


class CrowConan(ConanFile):
    name = "crowcpp-crow"
    homepage = "http://crowcpp.org/"
    description = "Crow is a C++ microframework for running web services."
    topics = ("web", "microframework", "header-only")
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "compiler", "arch", "build_type"
    license = "BSD-3-Clause"

    provides = "crow"

    options = {
        "amalgamation": [True, False],
    }
    default_options = {
        "amalgamation": False,
    }

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def export_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def requirements(self):
        self.requires("boost/1.77.0")
        if self.version == "0.2":
            self.requires("openssl/1.1.1l")

    def source(self):
        tools.files.get(self, 
            **self.conan_data["sources"][self.version],
            strip_root=True,
            destination=self._source_subfolder
        )

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)

        if self.options.amalgamation:
            cmake = CMake(self)
            cmake.definitions["BUILD_EXAMPLES"] = False
            cmake.definitions["BUILD_TESTING"] = False
            cmake.configure(source_folder=self._source_subfolder)
            cmake.build(target="amalgamation")

    def package(self):
        self.copy(pattern="LICENSE*", dst="licenses", src=self._source_subfolder)

        if self.options.amalgamation:
            self.copy("crow_all.h", dst="include")
        else:
            self.copy(
                "*.h",
                dst=os.path.join("include"),
                src=os.path.join(self._source_subfolder, "include"),
            )
            self.copy(
                "*.hpp",
                dst=os.path.join("include"),
                src=os.path.join(self._source_subfolder, "include"),
            )

    def package_id(self):
        self.info.settings.clear()

    def package_info(self):
        # These are not official targets, this is just the name (without fork prefix)
        self.cpp_info.names["cmake_find_package"] = "crow"
        self.cpp_info.names["cmake_find_package_multi"] = "crow"

        if self.settings.os in ("FreeBSD", "Linux"):
            self.cpp_info.system_libs = ["pthread"]
