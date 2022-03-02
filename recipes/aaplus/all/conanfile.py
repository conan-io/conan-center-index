from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import functools
import os

required_conan_version = ">=1.33.0"


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

    generators = "cmake"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def export_sources(self):
        self.copy("CMakeLists.txt")
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

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
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, "17")

        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        compiler_version = tools.Version(self.settings.compiler.version)
        if minimum_version and tools.Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                "{} requires C++17, which your compiler does not support.".format(self.name)
            )

        if self.settings.compiler == "clang" and (compiler_version >= "10" and compiler_version < "12"):
            raise ConanInvalidConfiguration(
                "AA+ cannot handle clang 10 and 11 due to filesystem being under experimental namespace"
            )

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder)

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.configure()
        return cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        tools.save(os.path.join(self.package_folder, "licenses", "LICENSE"), self._extract_license())
        cmake = self._configure_cmake()
        cmake.install()

    def _extract_license(self):
        aaplus_header = tools.load(os.path.join(self._source_subfolder, "AA+.h"))
        begin = aaplus_header.find("Copyright")
        end = aaplus_header.find("*/", begin)
        return aaplus_header[begin:end]

    def package_info(self):
        self.cpp_info.libs = ["aaplus"]
        if not self.options.shared:
            if self.settings.os == "Windows":
                self.cpp_info.system_libs.append("ws2_32")
            if self.settings.compiler == "gcc" and tools.Version(self.settings.compiler.version) < "9":
                self.cpp_info.system_libs.append("stdc++fs")
