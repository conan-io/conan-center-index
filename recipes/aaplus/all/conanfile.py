from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, get, load, save
from conan.tools.scm import Version
import os

required_conan_version = ">=1.50.0"


class Aaplusconan(ConanFile):
    name = "aaplus"
    description = (
        "AA+ is a C++ implementation for the algorithms as presented in the "
        "book \"Astronomical Algorithms\" by Jean Meeus"
    )
    license = "Unlicense"
    topics = ("aa+", "astronomy", "astronomical-algorithms", "orbital-mechanics")
    homepage = "http://www.naughter.com/aa.html"
    url = "https://github.com/conan-io/conan-center-index"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    def export_sources(self):
        for p in self.conan_data.get("patches", {}).get(self.version, []):
            copy(self, p["patch_file"], self.recipe_folder, self.export_sources_folder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "8",
            "clang": "9",
            "apple-clang": "11",
            "Visual Studio": "16",
        }

    def validate(self):
        if self.info.settings.compiler.cppstd:
            check_min_cppstd(self, "17")

        minimum_version = self._compilers_minimum_version.get(str(self.info.settings.compiler), False)
        compiler_version = Version(self.info.settings.compiler.version)
        if minimum_version and Version(self.info.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                "{} requires C++17, which your compiler does not support.".format(self.name)
            )

        if self.info.settings.compiler == "clang" and (compiler_version >= "10" and compiler_version < "12"):
            raise ConanInvalidConfiguration(
                "AA+ cannot handle clang 10 and 11 due to filesystem being under experimental namespace"
            )

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], destination=self.source_folder)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        save(self, os.path.join(self.package_folder, "licenses", "LICENSE"), self._extract_license())
        cmake = CMake(self)
        cmake.install()

    def _extract_license(self):
        aaplus_header = load(self, os.path.join(self.source_folder, "AA+.h"))
        begin = aaplus_header.find("Copyright")
        end = aaplus_header.find("*/", begin)
        return aaplus_header[begin:end]

    def package_info(self):
        self.cpp_info.libs = ["aaplus"]
        if not self.options.shared:
            if self.settings.os == "Windows":
                self.cpp_info.system_libs.append("ws2_32")
            if self.settings.compiler == "gcc" and Version(self.settings.compiler.version) < "9":
                self.cpp_info.system_libs.append("stdc++fs")
