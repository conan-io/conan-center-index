from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.microsoft import check_min_vs, is_msvc
from conan.tools.files import (
    apply_conandata_patches,
    export_conandata_patches,
    get,
    copy,
    rmdir,
)
from conan.tools.build import check_min_cppstd
from conan.tools.scm import Version
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
import os


required_conan_version = ">=1.53.0"


class MBitsArgsConan(ConanFile):
    name = "mbits-args"
    description = (
        "Small open-source library for program argument parser, inspired by Python's `argparse`, "
        "depending only on the standard library, with C++17 as minimum requirement."
    )
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/mbits-libs/args"
    topics = (
        "command-line",
        "commandline",
        "commandline-interface",
        "program-arguments",
        "argparse",
        "argparser",
        "argument-parsing",
    )
    settings = "os", "compiler", "build_type", "arch"
    options = {"fPIC": [True, False]}
    default_options = {"fPIC": True}

    @property
    def _min_cppstd(self):
        return 17

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "8",
            "clang": "12",
            "Visual Studio": "16",
            "msvc": "192",
            "apple-clang": "10.0",
        }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def layout(self):
        cmake_layout(self, src_folder="src")

    def validate(self):
        if self.settings.get_safe("compiler.cppstd"):
            check_min_cppstd(self, self._min_cppstd)
        check_min_vs(self, 192)
        if not is_msvc(self):
            minimum_version = self._compilers_minimum_version.get(
                str(self.settings.compiler), False
            )
            if (
                minimum_version
                and Version(self.settings.compiler.version) < minimum_version
            ):
                raise ConanInvalidConfiguration(
                    f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
                )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["LIBARGS_TESTING"] = False
        tc.variables["LIBARGS_INSTALL"] = True
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(
            self,
            pattern="LICENSE",
            dst=os.path.join(self.package_folder, "licenses"),
            src=self.source_folder,
        )
        cmake = CMake(self)
        cmake.install()

        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.libs = ["args"]

        self.cpp_info.set_property("cmake_file_name", "mbits-args")
        self.cpp_info.set_property("cmake_target_name", "mbits::args")

        self.cpp_info.filenames["cmake_find_package"] = "mbits-args"
        self.cpp_info.filenames["cmake_find_package_multi"] = "mbits-args"
        self.cpp_info.names["cmake_find_package"] = "mbits"
        self.cpp_info.names["cmake_find_package_multi"] = "mbits"
        self.cpp_info.components["args"].set_property(
            "cmake_target_name", "mbits::args"
        )
        self.cpp_info.components["args"].libs = ["args"]
