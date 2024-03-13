from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os
from conan.tools.build import check_min_cppstd
from conan.tools.files import get, copy
from conan.tools.layout import basic_layout
from conan.tools.scm import Version

import os
import sys

required_conan_version = ">=1.53.0"


class MetalcppConan(ConanFile):
    name = "metal-cpp"
    description = (
        "Library for the usage of Apple Metal GPU programming in C++ applications - "
        "Header-only library to wrap Metal in C++ classes"
    )
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://developer.apple.com/metal/cpp/"
    topics = ("metal", "gpu", "apple", "header-only")

    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    @property
    def _min_cppstd(self):
        return 17

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def validate(self):
        if not is_apple_os(self):
            raise ConanInvalidConfiguration(f"Metal can only be used on an Apple OS.")

        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        copy(
            self,
            pattern="LICENSE*",
            dst=os.path.join(self.package_folder, "licenses"),
            src=os.path.join(self.source_folder)
        )
        copy(
            self,
            pattern="**.hpp",
            dst=os.path.join(self.package_folder, "include"),
            src=os.path.join(self.source_folder),
            keep_path=True
        )

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []

        self.cpp_info.set_property("pkg_config_name", "metal-cpp")

        # TODO: Clarify if we need framework linking here
        # Also it could have a c++ file to get the actual implementation, but
        # depending on the needs this can be done without defining all the implementation
