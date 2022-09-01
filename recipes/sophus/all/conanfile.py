from conan import ConanFile
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout
from conan.tools.scm import Version
import os

required_conan_version = ">=1.50.0"


class SophusConan(ConanFile):
    name = "sophus"
    description = "C++ implementation of Lie Groups using Eigen."
    topics = ("eigen", "numerical", "math")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://strasdat.github.io/Sophus/"
    license = "MIT"
    no_copy_source = True

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "with_fmt": [True, False],
    }
    default_options = {
        "with_fmt": True,
    }

    def requirements(self):
        self.requires("eigen/3.4.0")
        if self.options.with_fmt and Version(self.version) >= Version("22.04.1"):
            self.requires("fmt/8.1.1")

    def package_id(self):
        self.info.clear()

    def layout(self):
        basic_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def package(self):
        copy(self, "LICENSE.txt", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "*.hpp", src=os.path.join(self.source_folder, "sophus"),
                            dst=os.path.join(self.package_folder, "include", "sophus"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "Sophus")
        self.cpp_info.set_property("cmake_target_name", "Sophus::Sophus")
        self.cpp_info.set_property("pkg_config_name", "sophus")
        self.cpp_info.bindirs = []
        self.cpp_info.frameworkdirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.resdirs = []
        if not self.options.with_fmt:
            self.cpp_info.defines.append("SOPHUS_USE_BASIC_LOGGING=1")

        # TODO: remove this block if required_conan_version changed to 1.51.1 or higher
        #       (see https://github.com/conan-io/conan/pull/11790)
        self.cpp_info.requires = ["eigen::eigen"]
        if self.options.with_fmt and Version(self.version) >= Version("22.04.1"):
            self.cpp_info.requires.append("fmt::fmt")

        # TODO: to remove in conan v2 once cmake_find_package* generator removed
        self.cpp_info.names["cmake_find_package"] = "Sophus"
        self.cpp_info.names["cmake_find_package_multi"] = "Sophus"
