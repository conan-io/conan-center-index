from conans import ConanFile, tools, CMake
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

    exports_sources = ["patches/**", ]

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def requirements(self):
        self.requires("boost/1.77.0")
        if self.version == "0.2":
            self.requires("openssl/1.1.1l")

    def source(self):
        tools.get(
            **self.conan_data["sources"][self.version],
            strip_root=True,
            destination=self._source_subfolder
        )

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)

        cmake = CMake(self)
        cmake.definitions["BUILD_EXAMPLES"] = False
        cmake.definitions["BUILD_TESTING"] = False
        cmake.configure(source_folder=self._source_subfolder)
        cmake.build(target="amalgamation")

    def package(self):
        self.copy(pattern="LICENSE*", dst="licenses", src=self._source_subfolder)
        self.copy(
            "*.h",
            dst=os.path.join("include", "crow"),
            src=os.path.join(self._source_subfolder, "include"),
        )
        self.copy("crow_all.h", dst=os.path.join("include", "crow"))

    def package_id(self):
        self.info.header_only()

    def package_info(self):
        # These are not official targets, this is just the name (without fork prefix)
        self.cpp_info.names["cmake_find_package"] = "crow"
        self.cpp_info.names["cmake_find_package_multi"] = "crow"

        if self.settings.os in ("FreeBSD", "Linux"):
            self.cpp_info.system_libs = ["pthread"]
