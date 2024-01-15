from conan import ConanFile
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout
from conan.tools.scm import Version
import os

required_conan_version = ">=1.53.0"


class SophusConan(ConanFile):
    name = "sophus"
    description = "C++ implementation of Lie Groups using Eigen."
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://strasdat.github.io/Sophus/"
    topics = ("eigen", "numerical", "math", "header-only")
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "with_fmt": [True, False],
    }
    default_options = {
        "with_fmt": True,
    }
    no_copy_source = True

    def configure(self):
        if Version(self.version) < "1.22.4":
            del self.options.with_fmt

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("eigen/3.4.0", transitive_headers=True)
        if self.options.get_safe("with_fmt"):
            if Version(self.version) >= "1.22.10":
                self.requires("fmt/10.1.0", transitive_headers=True)
            else:
                self.requires("fmt/8.1.1", transitive_headers=True)

    def package_id(self):
        self.info.clear()

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        copy(self, "LICENSE.txt", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "*.hpp", src=os.path.join(self.source_folder, "sophus"),
                            dst=os.path.join(self.package_folder, "include", "sophus"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "Sophus")
        self.cpp_info.set_property("cmake_target_name", "Sophus::Sophus")
        self.cpp_info.set_property("pkg_config_name", "sophus")
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
        if self.options.get_safe("with_fmt") == False:
            self.cpp_info.defines.append("SOPHUS_USE_BASIC_LOGGING=1")

        # TODO: to remove in conan v2 once cmake_find_package* generator removed
        self.cpp_info.names["cmake_find_package"] = "Sophus"
        self.cpp_info.names["cmake_find_package_multi"] = "Sophus"
