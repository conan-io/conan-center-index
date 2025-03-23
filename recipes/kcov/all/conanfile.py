import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rmdir, rm
from conan.tools.scm import Version

required_conan_version = ">=1.53.0"


class KcovConan(ConanFile):
    name = "kcov"
    description = (
        "Code coverage tool for compiled programs, Python and Bash which uses "
        "debugging information to collect and report data without special compilation options"
    )
    license = "GPL-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://simonkagstrom.github.io/kcov/index.html"
    topics = ("coverage", "linux", "debug")

    package_type = "application"
    settings = "os", "arch", "compiler", "build_type"

    def export_sources(self):
        export_conandata_patches(self)
        copy(self, "conan_deps.cmake", self.recipe_folder, os.path.join(self.export_sources_folder, "src"))

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("zlib/[>=1.2.11 <2]")
        self.requires("libcurl/[>=7.78 <9]")
        self.requires("openssl/[>=1.1 <4]")
        if is_apple_os(self):
            self.requires("libdwarf/0.8.0")
        else:
            self.requires("elfutils/0.190")

    def package_id(self):
        del self.info.settings.compiler
        del self.info.settings.build_type

    def validate(self):
        if self.settings.os == "Windows":
            raise ConanInvalidConfiguration("kcov can not be built on windows.")
        if is_apple_os(self):
            if Version(self.version) < 42:
                # MachO support was added in v42
                raise ConanInvalidConfiguration(f"{self.ref} does not support {self.settings.os}.")
            if self.settings.arch == "armv8":
                # https://github.com/SimonKagstrom/kcov/blob/v42/cmake/TargetArch.cmake
                raise ConanInvalidConfiguration(f"{self.ref} does not support {self.settings.arch}.")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["CMAKE_PROJECT_kcov_INCLUDE"] = "conan_deps.cmake"
        tc.generate()
        deps = CMakeDeps(self)
        # Match Find*.cmake module names used by the project
        deps.set_property("libbfd", "cmake_file_name", "Bfd")
        deps.set_property("libdwarf", "cmake_file_name", "Dwarfutils")
        deps.set_property("elfutils", "cmake_file_name", "ElfUtils")
        deps.set_property("libcrpcut", "cmake_file_name", "LibCRPCUT")
        deps.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)
        # Disable project Find*.cmake modules just in case
        rm(self, "Find*.cmake", os.path.join(self.source_folder, "cmake"))

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "COPYING*", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.includedirs = []
        self.cpp_info.frameworkdirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.resdirs = []

        # TODO: to remove in conan v2
        bindir = os.path.join(self.package_folder, "bin")
        self.env_info.PATH.append(bindir)
