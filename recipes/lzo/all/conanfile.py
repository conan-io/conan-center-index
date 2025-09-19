from conan import ConanFile
from conan.errors import ConanException
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir
from conan.tools.scm import Version
import os

required_conan_version = ">=2.4"


class LZOConan(ConanFile):
    name = "lzo"
    description = "lzo is a portable lossless data compression library written in ANSI C"
    license = "GPL-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://www.oberhumer.com/opensource/lzo/"
    topics = ("compression",)

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    implements = ["auto_shared_fpic"]
    languages = "C"

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["ENABLE_STATIC"] = not self.options.shared
        tc.variables["ENABLE_SHARED"] = self.options.shared
        if Version(self.version) > "2.10":
            raise ConanException("CMake Minimumversion hardcoded to 3.5, please check and update in newer versions")
        tc.cache_variables["CMAKE_POLICY_VERSION_MINIMUM"] = "3.5"  # CMake 4 support
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "bin", "lzo"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "lzo2")
        self.cpp_info.includedirs.append(os.path.join("include", "lzo"))
        self.cpp_info.libs = ["lzo2"]
