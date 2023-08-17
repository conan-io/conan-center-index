from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps
from conan.tools.files import get, copy, rmdir
from conan.tools.layout import basic_layout
from conan.errors import ConanInvalidConfiguration
from conan.tools.microsoft import check_min_vs, is_msvc
from conan.tools.scm import Version
import os

required_conan_version = ">=1.50.0"

class LogrConan(ConanFile):
    name = "logr"
    description = (
        "Logger frontend substitution for spdlog, glog, etc "
        "for server/desktop applications"
    )
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/ngrodzitski/logr"
    topics = ("logger", "development", "util", "utils")
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "backend": ["spdlog", "glog", "log4cplus", "boostlog", None],
    }
    default_options = {
        "backend": "spdlog",
    }

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        if self.options.backend != "spdlog":
            fmt_ref = "fmt/10.0.0"
        elif Version(self.version) >= "0.6.0":
            fmt_ref = "fmt/9.1.0"
            spdlog_ref = "spdlog/1.11.0"
        else:
            fmt_ref = "fmt/8.1.1"
            spdlog_ref = "spdlog/1.10.0"

        self.requires(fmt_ref)

        if self.options.backend == "spdlog":
            self.requires(spdlog_ref)
        elif self.options.backend == "glog":
            self.requires("glog/0.6.0")
        elif self.options.backend == "log4cplus":
            self.requires("log4cplus/2.1.0")
        elif self.options.backend == "boostlog":
            self.requires("boost/1.82.0")

    def package_id(self):
        self.info.settings.clear()
        self.info.requires.clear()

    def validate(self):
        minimal_cpp_standard = "17"
        if self.settings.get_safe("compiler.cppstd"):
            check_min_cppstd(self, minimal_cpp_standard)
        minimal_version = {
            "gcc": "10",
            "clang": "11",
            "apple-clang": "12",
        }
        check_min_vs(self, 192)
        if not is_msvc(self):
            minimum_version = minimal_version.get(str(self.settings.compiler), False)
            if minimum_version and Version(self.settings.compiler.version) < minimum_version:
                raise ConanInvalidConfiguration(
                    f"{self.ref} requires minimum {self.settings.compiler}-{minimum_version}."
                )

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["LOGR_WITH_SPDLOG_BACKEND"] = (
            self.options.backend == "spdlog"
        )
        tc.variables["LOGR_WITH_GLOG_BACKEND"] = (
            self.options.backend == "glog"
        )
        tc.variables["LOGR_WITH_LOG4CPLUS_BACKEND"] = (
            self.options.backend == "log4cplus"
        )
        tc.variables["LOGR_WITH_BOOSTLOG_BACKEND"] = (
            self.options.backend == "boostlog"
        )
        tc.variables["LOGR_INSTALL"] = True
        tc.variables["LOGR_CONAN_PACKAGING"] = True
        tc.variables["LOGR_BUILD_TESTS"] = False
        tc.variables["LOGR_BUILD_EXAMPLES"] = False
        tc.variables["LOGR_BUILD_BENCHMARKS"] = False
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
                destination=self.source_folder, strip_root=True)

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.configure(build_script_folder=os.path.join(self.source_folder, "logr"))
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib"))

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.frameworkdirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.set_property("cmake_file_name", "logr")

        self.cpp_info.names["cmake_find_package"] = "logr"
        self.cpp_info.names["cmake_find_package_multi"] = "logr"

        self.cpp_info.components["logr_base"].includedirs = ["include"]
        self.cpp_info.components["logr_base"].requires = ["fmt::fmt"]

        if self.options.backend == "spdlog":
            self.cpp_info.components["logr_spdlog"].includedirs = []
            self.cpp_info.components["logr_spdlog"].requires = [
                "logr_base",
                "spdlog::spdlog",
            ]
        elif self.options.backend == "glog":
            self.cpp_info.components["logr_glog"].includedirs = []
            self.cpp_info.components["logr_glog"].requires = [
                "logr_base",
                "glog::glog",
            ]
        elif self.options.backend == "log4cplus":
            self.cpp_info.components["logr_log4cplus"].includedirs = []
            self.cpp_info.components["logr_log4cplus"].requires = [
                "logr_base",
                "log4cplus::log4cplus",
            ]
        elif self.options.backend == "boostlog":
            self.cpp_info.components["logr_boostlog"].includedirs = []
            self.cpp_info.components["logr_boostlog"].requires = [
                "logr_base",
                "boost::log",
            ]
