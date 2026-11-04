from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout
import os

required_conan_version = ">=1.53.0"

class DylibConan(ConanFile):
    name = "dylib"
    homepage = "https://github.com/martin-olivier/dylib"
    url = "https://github.com/conan-io/conan-center-index"
    description = "C++ cross-platform wrapper around dynamic loading of shared libraries (dll, so, dylib)"
    license = "MIT"
    topics = ("shared-library", "cross-platform", "header-only")

    package_type = 'header-library'
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        pass

    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, 11)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def build(self):
        pass

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "dylib.hpp", src=os.path.join(self.source_folder, "include"), dst=os.path.join(self.package_folder, "include"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "dylib")
        self.cpp_info.set_property("cmake_target_name", "dylib::dylib")
        self.cpp_info.set_property("pkg_config_name", "dylib")
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["dl"])
