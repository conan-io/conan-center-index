import shutil
import os
from conans.tools import download
from conans.tools import unzip
from conans.tools import check_md5
from conans.tools import check_sha1
from conans.tools import check_sha256
from conans import ConanFile
from conans import tools
from conans import CMake


class ConfuBoostConan(ConanFile):
    name = "confu_boost"
    version = "1.0.0"
    license = "BSL-1.0"
    homepage = "https://github.com/werto87/confu_boost"
    url = "https://github.com/conan-io/conan-center-index"
    description = "convenience functions \
        for reducing boilerplate while working with boost"
    topics = ("boost boilerplate")
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    generators = "cmake"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def requirements(self):
        self.requires("boost/1.76.0")
        self.requires("catch2/2.13.1")

    def build(self):
        cmake = CMake(self)
        cmake.configure(source_folder="confu_boost-" + self.version)
        cmake.build()

    def package(self):
        self.copy("*.h*", dst="include/confu_boost",
                  src="confu_boost-" + self.version + "/confu_boost")
        self.copy("*.dll", dst="bin", keep_path=False)
        self.copy("*.so", dst="lib", keep_path=False)
        self.copy("*.dylib", dst="lib", keep_path=False)
        self.copy("*.a", dst="lib", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = ["confuBoost"]
