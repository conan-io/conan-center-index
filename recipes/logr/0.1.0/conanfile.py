from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.microsoft import check_min_vs, is_msvc_static_runtime, is_msvc
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get, copy, rmdir
from conan.tools.build import check_min_cppstd
from conan.tools.scm import Version
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
import os

required_conan_version = ">=1.53.0"

class LogrConan(ConanFile):
    name = "logr"
    description = "Logger frontend substitution for spdlog, glog, etc for server/desktop applications"
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/ngrodzitski/logr"
    topics = ("logger", "development", "util", "utils")
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "backend": ["spdlog", "glog", "log4cplus", "log4cplus-unicode", None],
    }
    default_options = {
        "backend": "spdlog",
    }

    @property
    def _min_cppstd(self):
        return 17

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "7",
            "clang": "7",
            "apple-clang": "10",
            "Visual Studio": "16",
            "msvc": "192",
        }

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("fmt/10.2.0")
        if self.options.backend == "spdlog":
            self.requires("spdlog/1.13.0")
        elif self.options.backend == "glog":
            self.requires("glog/0.6.0")
        elif self.options.backend in ["log4cplus", "log4cplus-unicode"]:
            self.requires("log4cplus/2.1.1")

    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )
        if self.options.backend == "log4cplus" and self.options["log4cplus"].unicode:
            raise ConanInvalidConfiguration("backend='log4cplus' requires log4cplus:unicode=False")
        elif self.options.backend == "log4cplus-unicode" and not self.options["log4cplus"].unicode:
            raise ConanInvalidConfiguration("backend='log4cplus-unicode' requires log4cplus:unicode=True")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["LOGR_WITH_SPDLOG_BACKEND"] = self.options.backend == "spdlog"
        tc.cache_variables["LOGR_WITH_GLOG_BACKEND"] = self.options.backend == "glog"
        tc.cache_variables["LOGR_WITH_LOG4CPLUS_BACKEND"] = self.options.backend in ["log4cplus", "log4cplus-unicode"]
        tc.cache_variables["LOGR_INSTALL"] = True
        tc.cache_variables["LOGR_BUILD_TESTS"] = False
        tc.cache_variables["LOGR_BUILD_EXAMPLES"] = False
        tc.cache_variables["LOGR_BUILD_BENCHMARKS"] = False
        tc.generate()
        dpes = CMakeDeps(self)
        dpes.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()

        rmdir(self, os.path.join(self.package_folder, "lib"))

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
