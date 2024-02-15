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
    package_type = "header-library"
    options = {
        "with_spdlog_backend": [True, False],
        "with_glog_backend": [True, False],
        "with_log4cplus_backend": [True, False],
        "with_boostlog_backend": [True, False],
    }
    default_options = {
        "with_spdlog_backend": True,
        "with_glog_backend": False,
        "with_log4cplus_backend": False,
        "with_boostlog_backend": False,
    }

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("fmt/10.2.1")

        if self.options.with_spdlog_backend:
            self.requires("spdlog/1.12.0")

        if self.options.with_glog_backend:
            self.requires("glog/0.6.0")

        if self.options.with_log4cplus_backend:
            self.requires("log4cplus/2.1.0")

        if self.options.with_boostlog_backend:
            self.requires("boost/1.83.0")

    def package_id(self):
        self.info.settings.clear()

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

        include_folder = os.path.join(self.package_folder, "include", "logr")
        if not self.options.with_spdlog_backend:
            rm(self, "spdlog_backend.hpp", include_folder)

        if not self.options.with_glog_backend:
            rm(self, "glog_backend.hpp", include_folder)

        if not self.options.with_log4cplus_backend:
            rm(self, "log4cplus_backend.hpp", include_folder)

        if not self.options.with_boostlog_backend:
            rm(self, "boostlog_backend.hpp", include_folder)

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []


        self.cpp_info.components["logr_base"].includedirs = ["include"]
        self.cpp_info.components["logr_base"].requires = ["fmt::fmt"]

        if self.options.with_spdlog_backend:
            self.cpp_info.components["logr_spdlog"].includedirs = []
            self.cpp_info.components["logr_spdlog"].requires = [
                "logr_base",
                "spdlog::spdlog",
            ]

        if self.options.with_glog_backend:
            self.cpp_info.components["logr_glog"].includedirs = []
            self.cpp_info.components["logr_glog"].requires = [
                "logr_base",
                "glog::glog",
            ]

        if self.options.with_log4cplus_backend:
            self.cpp_info.components["logr_log4cplus"].includedirs = []
            self.cpp_info.components["logr_log4cplus"].requires = [
                "logr_base",
                "log4cplus::log4cplus",
            ]

        if self.options.with_boostlog_backend:
            self.cpp_info.components["logr_boostlog"].includedirs = []
            self.cpp_info.components["logr_boostlog"].requires = [
                "logr_base",
                "boost::log",
            ]
