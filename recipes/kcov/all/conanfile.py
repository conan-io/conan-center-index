import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rmdir, rm, replace_in_file

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

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("zlib/[>=1.2.11 <2]")
        self.requires("libiberty/9.1.0")
        self.requires("libcurl/[>=7.78 <9]")
        self.requires("libelf/0.8.13")
        self.requires("elfutils/0.190")
        self.requires("libdwarf/0.8.0")

    def package_id(self):
        del self.info.settings.compiler
        del self.info.settings.build_type

    def validate(self):
        if self.settings.os == "Windows":
            raise ConanInvalidConfiguration("kcov can not be built on windows.")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.generate()
        deps = CMakeDeps(self)
        deps.set_property("libdwarf", "cmake_file_name", "Dwarfutils")
        deps.set_property("elfutils", "cmake_file_name", "Elfutils")
        deps.generate()

    def build(self):
        apply_conandata_patches(self)
        rm(self, "Find*.cmake", os.path.join(self.source_folder, "cmake"))
        src_cmakelists = os.path.join(self.source_folder, "src", "CMakeLists.txt")
        # Optional dependency, not available on CCI
        replace_in_file(self, src_cmakelists, "find_package (Bfd)", "")
        # Fix LibElf and ElfUtils capitalization
        replace_in_file(self, src_cmakelists, "find_package (LibElf)", "find_package (LIBELF REQUIRED CONFIG)")
        replace_in_file(self, src_cmakelists, "ElfUtils", "Elfutils", strict=False)
        replace_in_file(self, src_cmakelists, "${LIBELF_LIBRARIES}", "${LIBELF_LIBRARIES} ${Elfutils_LIBRARIES}")
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "share"))
        copy(self, "COPYING*", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)

    def package_info(self):
        self.cpp_info.includedirs = []
        self.cpp_info.frameworkdirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.resdirs = []

        # TODO: to remove in conan v2
        bindir = os.path.join(self.package_folder, "bin")
        self.env_info.PATH.append(bindir)
