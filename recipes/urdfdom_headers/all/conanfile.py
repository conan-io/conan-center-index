from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout
import os

required_conan_version = ">=1.52.0"


class PackageConan(ConanFile):
    name = "urdfdom_headers"
    description = "Headers for URDF parsers"
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/ros/urdfdom_headers"
    topics = ("urdf", "ros", "robotics")

    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, 11)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        # Add a project prefix to the headers to match the default APPEND_PROJECT_NAME_TO_INCLUDEDIR=ON
        copy(self, "*.h",
             os.path.join(self.source_folder, "include"),
             os.path.join(self.package_folder, "include", "urdfdom"))

    def package_info(self):
        self.cpp_info.includedirs.append(os.path.join("include", "urdfdom"))
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
