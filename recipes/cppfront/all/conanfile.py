from conan import ConanFile
from conan.tools.files import save

from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps, cmake_layout
from conan.tools.build import check_min_cppstd
from conan.tools.scm import Version
from conan.tools.files import apply_conandata_patches, copy, get, patch, rmdir

import os
import textwrap



required_conan_version = ">=1.52.0"

class CppfrontConan(ConanFile):
    name = "cppfront"
    description = "Cppfront is a experimental compiler from a potential C++ 'syntax 2' (Cpp2) to today's 'syntax 1' (Cpp1)"
    topics = ("cppfront", "c++2", "build-system")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/hsutter/cppfront"
    license = "CC-BY-NC-ND-4.0"
    settings = "os", "arch", "compiler", "build_type"
    # no_copy_source = True

    # generators = "cmake"

    # @property
    # def _settings_build(self):
    #     return getattr(self, "settings_build", self.settings)

    # def requirements(self):
    #     self.requires("ninja/1.11.0")

    # def package_id(self):
    #     self.info.clear()

    def layout(self):
        cmake_layout(self, src_folder="src")

    def export_sources(self):
        # self.copy("CMakeLists.txt")
        # copy(self, "CMakeLists.txt", self.recipe_folder, self.export_sources_folder)
        copy(self, "CMakeLists.txt", self.recipe_folder, os.path.join(self.export_sources_folder, "src"))

    def source(self):
        get(self, **self.conan_data["sources"][self.version], destination=self.source_folder, strip_root=True)

    # def generate(self):
    #     tc = CMakeToolchain(self)
    #     # tc.variables["BUILD_TESTING"] = False
    #     tc.generate()

    def generate(self):
        tc = CMakeToolchain(self)
        tc.generate()
        tc = CMakeDeps(self)
        tc.generate()


    def build(self):
        # apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "*", src=self.source_folder, dst=os.path.join(self.package_folder, "bin"))
        rmdir(self, os.path.join(self.package_folder, "bin", "test cases"))

        cmake = CMake(self)
        cmake.install()

        # # create wrapper scripts
        # save(self, os.path.join(self.package_folder, "bin", "meson.cmd"), textwrap.dedent("""\
        #     @echo off
        #     CALL python %~dp0/meson.py %*
        # """))
        # save(self, os.path.join(self.package_folder, "bin", "meson"), textwrap.dedent("""\
        #     #!/usr/bin/env bash
        #     meson_dir=$(dirname "$0")
        #     exec "$meson_dir/meson.py" "$@"
        # """))

    @staticmethod
    def _chmod_plus_x(filename):
        if os.name == "posix":
            os.chmod(filename, os.stat(filename).st_mode | 0o111)

    def package_info(self):
        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info(f"Appending PATH environment variable: {bin_path}")
        self.env_info.PATH.append(bin_path)

        # self._chmod_plus_x(os.path.join(bin_path, "cppfront"))
        # self.cpp_info.builddirs = [os.path.join("bin", "cppfrontbuild", "cmake", "data")]

        bin_ext = ".exe" if self.settings.os == "Windows" else ""
        cppfront_bin = os.path.join(self.package_folder, "bin", "cppfront{}".format(bin_ext)).replace("\\", "/")

        # M4 environment variable is used by a lot of scripts as a way to override a hard-coded embedded m4 path
        self.output.info("Setting M4 environment variable: {}".format(cppfront_bin))
        self.env_info.cppfront = cppfront_bin

        self.cpp_info.frameworkdirs = []
        self.cpp_info.includedirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.resdirs = []

