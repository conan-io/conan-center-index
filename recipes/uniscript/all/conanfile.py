# Conan 2 recipe of the native C library (c/native) and the header-only C++17 wrapper, built with c/CMakeLists.txt from
# the release tarball `make -C c/native dist`. Laid out as conan-center-index's recipes/uniscript, which is also a
# local-recipes-index remote: conan remote add uniscript <checkout>/packaging/conan --type local-recipes-index
# At a release: url and sha256 in conandata.yml, the version in config.yml (notes/c-packaging.md).
import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir
from conan.tools.microsoft import is_msvc

required_conan_version = ">=2.0"


class UniscriptConan(ConanFile):
    name = "uniscript"
    description = "ASCII names for Unicode text (<:alpha> -> alpha) and back: C11 library, header-only C++17 wrapper"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/pannous/uniscript"
    topics = ("unicode", "entities", "text", "encoding", "math")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        # a C library: uniscript.hpp is header-only and compiled by the consumer
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def validate(self):
        if is_msvc(self):
            raise ConanInvalidConfiguration(f"{self.ref} embeds its index with the assembler's .incbin: no MSVC")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        toolchain = CMakeToolchain(self)
        toolchain.cache_variables["UNISCRIPT_TESTS"] = False
        toolchain.cache_variables["UNISCRIPT_INSTALL"] = True
        toolchain.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure(build_script_folder="c")
        cmake.build()

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        CMake(self).install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.libs = ["uniscript"]
        self.cpp_info.set_property("cmake_file_name", "uniscript")
        self.cpp_info.set_property("cmake_target_name", "uniscript::uniscript")
        self.cpp_info.set_property("pkg_config_name", "uniscript")
