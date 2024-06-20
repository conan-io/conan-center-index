import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import copy, get, rmdir, replace_in_file, rename
from conan.tools.microsoft import is_msvc

required_conan_version = ">=1.53.0"


class OfeliConan(ConanFile):
    name = "ofeli"
    description = "An Object Finite Element Library"
    license = "LGPL-3.0-or-later"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://ofeli.org/index.html"
    topics = ("finite-element", "finite-element-library", "finite-element-analysis", "finite-element-solver")

    package_type = "static-library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "fPIC": [True, False],
    }
    default_options = {
        "fPIC": True,
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def layout(self):
        cmake_layout(self, src_folder="src")

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, 11)
        if self.settings.compiler in ["clang", "apple-clang"] or is_msvc(self):
            # Clang fails with
            # include/linear_algebra/LocalVect_impl.h:251:42: error: cannot initialize return object of type 'OFELI::Element *' with an lvalue of type 'const OFELI::Element *'
            # MSVC fails with a lot of errors
            # https://c3i.jfrog.io/c3i/misc/summary.html?json=https://c3i.jfrog.io/c3i/misc/logs/pr/18952/12-windows-visual_studio/ofeli/5.1.0/summary.json
            raise ConanInvalidConfiguration(f"{self.settings.compiler} is not supported due to compilation errors")

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.16 <4]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()
        tc = CMakeToolchain(self)
        tc.generate()

    def _patch_sources(self):
        cmakelists = os.path.join(self.source_folder, "CMakeLists.txt")
        replace_in_file(self, cmakelists, "add_subdirectory (demos)", "")
        replace_in_file(self, cmakelists, "add_subdirectory (util)", "")
        # Fix incorrect use of add_definitions() for build flags
        replace_in_file(self, cmakelists, "add_definitions", "add_compile_options")
        # Fix -fPIC support
        replace_in_file(self, cmakelists, " -fPIE", "")

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "COPYING", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()
        rename(self, os.path.join(self.package_folder, "share", "ofeli", "material"),
               os.path.join(self.package_folder, "res"))
        rmdir(self, os.path.join(self.package_folder, "share"))


    def package_info(self):
        self.cpp_info.libs = ["ofeli"]
        self.cpp_info.includedirs = [os.path.join("include", "ofeli")]
        res_path = os.path.join(self.package_folder, "res")
        self.runenv_info.define_path("OFELI_PATH_MATERIAL", res_path)
