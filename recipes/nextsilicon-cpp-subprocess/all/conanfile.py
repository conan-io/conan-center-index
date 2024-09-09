import os

from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout

required_conan_version = ">=1.52.0"


class CppSubprocess(ConanFile):
    name = "nextsilicon-cpp-subprocess"
    description = (
        "Subprocessing with modern C++. "
        "The only goal was to develop something that is as close as possible"
        " to the Python subprocess module in dealing with processes."
    )
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/nextsilicon/cpp-subprocess"
    topics = ("subprocess", "os", "fork", "header-only")

    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    @property
    def _min_cppstd(self):
        return 11

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        copy(self, "subprocess.hpp",
             dst=os.path.join(self.package_folder, "include/cpp-subprocess"),
             src=self.source_folder)
        copy(self, "LICENSE.MIT",
             dst=os.path.join(self.package_folder, "licenses"),
             src=self.source_folder)

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
