from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.files import get, copy,rm
from conan.tools.layout import basic_layout
from conan.tools.scm import Version
from conan.errors import ConanInvalidConfiguration
from conan.tools.microsoft import check_min_vs, is_msvc
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
        self.requires("fmt/10.1.1")

        if self.options.backend == "spdlog":
            self.requires("spdlog/1.12.0")
        elif self.options.backend == "glog":
            self.requires("glog/0.6.0")
        elif self.options.backend == "log4cplus":
            self.requires("log4cplus/2.1.0")
        elif self.options.backend == "boostlog":
            self.requires("boost/1.83.0")

    def package_id(self):
        self.info.clear()

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

    def build(self):
        pass

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
                destination=self.source_folder, strip_root=True)

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "*.*pp", src=os.path.join(self.source_folder, "logr", "include"), dst=os.path.join(self.package_folder, "include"))

        for back in ["spdlog", "glog", "log4cplus", "boostlog"]:
            if self.options.backend != back:
                rm(self, f"include/logr/{back}_backend.hpp", self.package_folder)

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
