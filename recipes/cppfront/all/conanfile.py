from conan import ConanFile

from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get
from conan.tools.microsoft import check_min_vs, is_msvc

import os

required_conan_version = ">=1.47.0"

class CppfrontConan(ConanFile):
    name = "cppfront"
    description = "Cppfront is a experimental compiler from a potential C++ 'syntax 2' (Cpp2) to today's 'syntax 1' (Cpp1)"
    topics = ("cpp2")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/hsutter/cppfront"
    license = "CC-BY-NC-ND-4.0"
    settings = "os", "arch", "compiler", "build_type"

    @property
    def _minimum_cpp_standard(self):
        return 20

    @property
    def _compilers_minimum_version(self):
        return {"gcc": "11",
                "Visual Studio": "16.9",
                "clang": "12",
                "apple-clang": "13",
                }

    def layout(self):
        cmake_layout(self, src_folder="src")

    def export_sources(self):
        copy(self, "CMakeLists.txt", self.recipe_folder, os.path.join(self.export_sources_folder, "src"))

    def source(self):
        get(self, **self.conan_data["sources"][self.version], destination=self.source_folder, strip_root=True)

    def validate(self):
        if self.info.settings.compiler.cppstd:
            check_min_cppstd(self, self._minimum_cpp_standard)

        def _lazy_lt_semver(v1, v2):
            lv1 = [int(v) for v in v1.split(".")]
            lv2 = [int(v) for v in v2.split(".")]
            min_length = min(len(lv1), len(lv2))
            return lv1[:min_length] < lv2[:min_length]

        check_min_vs(self, "192.9")
        if not is_msvc(self):
            minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
            if not minimum_version:
                self.output.warn(f"{self.name} {self.version} requires C++20. Your compiler is unknown. Assuming it supports C++20.")
            elif _lazy_lt_semver(str(self.settings.compiler.version), minimum_version):
                raise ConanInvalidConfiguration(f"{self.name} {self.version} requires C++20, which your compiler does not support.")
            if self.info.settings.compiler == "clang" and str(self.info.settings.compiler.version) in ("13", "14"):
                raise ConanInvalidConfiguration(f"{self.ref} currently does not work with Clang {self.info.settings.compiler.version} on CCI, it enters in an infinite build loop (smells like a compiler bug). Contributions are welcomed!")

    def generate(self):
        tc = CMakeToolchain(self)
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "cppfront*", src=self.source_folder, dst=os.path.join(self.package_folder, "bin"))
        copy(self, pattern="*.h", src=os.path.join(self.source_folder, "include"), dst=os.path.join(self.package_folder, "include"))

        cmake = CMake(self)
        cmake.install()

    @staticmethod
    def _chmod_plus_x(filename):
        if os.name == "posix":
            os.chmod(filename, os.stat(filename).st_mode | 0o111)

    def package_info(self):
        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info(f"Appending PATH environment variable: {bin_path}")
        self.env_info.PATH.append(bin_path)

        bin_ext = ".exe" if self.settings.os == "Windows" else ""
        cppfront_bin = os.path.join(self.package_folder, "bin", "cppfront{}".format(bin_ext)).replace("\\", "/")

        self.output.info("Setting CppFront environment variable: {}".format(cppfront_bin))
        self.env_info.cppfront = cppfront_bin

        self.cpp_info.frameworkdirs = []
        self.cpp_info.includedirs = [os.path.join(self.package_folder, "include")]
        self.cpp_info.libdirs = []
        self.cpp_info.resdirs = []

