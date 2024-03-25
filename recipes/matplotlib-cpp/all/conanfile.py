import os

from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout

required_conan_version = ">=1.53.0"


class MatplotlibCppConan(ConanFile):
    name = "matplotlib-cpp"
    description = "Extremely simple yet powerful header-only C++ plotting library built on the popular matplotlib"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/lava/matplotlib-cpp"

    topics = ("plotting", "matplotlib", "visualization")
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"

    @property
    def _min_cppstd(self):
        return 11

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        copy(self, "LICENSE.matplotlib", self.source_folder, os.path.join(self.package_folder, "licenses"))
        copy(self, "matplotlibcpp.h", self.source_folder, os.path.join(self.package_folder, "include"))

    def package_info(self):
        # https://github.com/lava/matplotlib-cpp/blob/master/cmake/matplotlib_cppConfig.cmake.in
        self.cpp_info.set_property("cmake_file_name", "matplotlib_cpp")
        self.cpp_info.set_property("cmake_target_name", "matplotlib_cpp::matplotlib_cpp")

        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
