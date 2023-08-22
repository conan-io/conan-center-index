import os

from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout


class libFieldConan(ConanFile):
    name = "libfield"
    description = "A C++ library for working with discretized field data (useful for a finite-difference heat solver for example)."
    url = "https://github.com/conan-io/conan-center-index"
    license = "MIT"
    topics = ["physics", "numerical analysis"]
    package_type = "header-library"
    homepage = "https://github.com/CD3/libField"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    def layout(self):
        basic_layout(self, src_folder="src")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, 11)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        copy(
            self,
            pattern="LICENSE.md",
            dst=os.path.join(self.package_folder, "licenses"),
            src=self.source_folder,
        )
        copy(
            self,
            "*.h",
            os.path.join(self.source_folder, "src"),
            os.path.join(self.package_folder, "include"),
        )
        copy(
            self,
            "*.hpp",
            os.path.join(self.source_folder, "src"),
            os.path.join(self.package_folder, "include"),
        )

    def package_id(self):
        self.info.clear()

    def package_info(self):
        # For header-only packages, libdirs and bindirs are not used
        # so it's necessary to set those as empty.
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []

        self.cpp_info.set_property("cmake_file_name", "libField")
        self.cpp_info.set_property("cmake_target_name", "libField::Field")
