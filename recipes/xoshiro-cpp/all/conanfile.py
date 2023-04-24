import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get
from conan.tools.scm import Version

required_conan_version = ">=1.53.0"


class XoshiroCppConan(ConanFile):
    name = "xoshiro-cpp"
    description = "Header-only Xoshiro/Xoroshiro PRNG wrapper library for modern C++ (C++17/C++20)"
    license = "MIT"
    homepage = "https://github.com/Reputeless/Xoshiro-cpp"
    url = "https://github.com/conan-io/conan-center-index"
    topics = ("prng", "xoshiro", "header-only")
    settings = "arch", "build_type", "compiler", "os"

    @property
    def _minimum_compilers_version(self):
        return {
            "apple-clang": "10",
            "clang": "6",
            "gcc": "7",
            "Visual Studio": "16"
        }

    @property
    def _minimum_cpp_standard(self):
        return 17

    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.settings.get_safe("compiler.cppstd"):
            check_min_cppstd(self, self._minimum_cpp_standard)

        compiler = str(self.settings.compiler)
        version = Version(self.settings.compiler.version)
        try:
            min_version = self._minimum_compilers_version[compiler]
            if version < min_version:
                msg = (
                    f"{self.name} requires C++{self._minimum_cpp_standard} features "
                    f"which are not supported by compiler {compiler} {version}."
                )
                raise ConanInvalidConfiguration(msg)
        except KeyError:
            msg = (
                f"{self.ref} recipe lacks information about the {compiler} compiler, "
                f"support for the required C++{self._minimum_cpp_standard} features is assumed"
            )
            self.output.warn(msg)

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def package(self):
        copy(self, "*.hpp", src=self.source_folder,
             dst=os.path.join(self.package_folder, "include/xoshiro-cpp/"))
        copy(self, "LICENSE", src=self.source_folder,
             dst=os.path.join(self.package_folder, "licenses"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "xoshiro-cpp")
        self.cpp_info.set_property(
            "cmake_target_name", "xoshiro-cpp::xoshiro-cpp")
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
