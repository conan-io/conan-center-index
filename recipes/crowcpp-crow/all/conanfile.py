from conans import ConanFile, tools, CMake
import os

required_conan_version = ">=1.33.0"


class CrowConan(ConanFile):
    name = "crowcpp-crow"
    homepage = "https://github.com/CrowCpp/crow"
    description = "Crow is a C++ microframework for running web services."
    topics = ("conan", "web", "microframework", "header-only")
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "compiler", "arch", "build_type"
    license = "BSD-3-Clause"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def requirements(self):
        self.requires("boost/1.75.0")
        if self.version == "0.2":
            self.requires("openssl/1.1.1k")

    def source(self):
        tools.get(
            **self.conan_data["sources"][self.version],
            strip_root=True,
            destination=self._source_subfolder
        )

    def build(self):
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
        if self.settings.os in ("FreeBSD", "Linux"):
            self.cpp_info.system_libs = ["pthread"]
