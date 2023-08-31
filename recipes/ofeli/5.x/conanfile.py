import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout
from conan.tools.files import copy, get, rmdir, replace_in_file

required_conan_version = ">=1.53.0"


class OfeliConan(ConanFile):
    name = "ofeli"
    description = "An Object Finite Element Library"
    license = "LGPL-3.0-or-later"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://ofeli.org/index.html"
    topics = ("finite-element", "finite-element-library", "finite-element-analysis", "finite-element-solver")

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

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def validate(self):
        if self.settings.os not in ["Linux", "FreeBSD"]:
            raise ConanInvalidConfiguration("Ofeli only supports Linux")
        if self.settings.compiler != "gcc":
            raise ConanInvalidConfiguration("Ofeli only supports GCC")
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, 11)
        if self.settings.compiler.libcxx != "libstdc++11":
            raise ConanInvalidConfiguration("Ofeli only supports libstdc++'s new ABI")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.generate()

    def _patch_sources(self):
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"),
                        "add_subdirectory (demos)", "")
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"),
                        "add_subdirectory (util)", "")

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "COPYING",
             dst=os.path.join(self.package_folder, "licenses"),
             src=os.path.join(self.source_folder, "doc"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "share", "ofeli", "doc"))
        rmdir(self, os.path.join(self.package_folder, "share", "ofeli", "demos"))
        rmdir(self, os.path.join(self.package_folder, "share", "ofeli", "util"))


    def package_info(self):
        self.cpp_info.libs = ["ofeli"]
        self.cpp_info.includedirs = [os.path.join("include", "ofeli")]
        res_path = os.path.join(self.package_folder, "share", "ofeli", "material")
        self.runenv_info.define_path("OFELI_PATH_MATERIAL", res_path)
