from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.files import get, copy
from conan.tools.layout import basic_layout

import os

required_conan_version = ">=2.0"


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

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def validate(self):
        os_name = str(self.settings.os)
        if not os_name in ["Macos", "iOS", "tvOS", "visionOS"]:
            raise ConanInvalidConfiguration("Metal can only be used on macOS, iOS, tvOS or visionOS.")

        check_min_cppstd(self, 17)

    def package(self):
        copy(
            self,
            pattern="LICENSE.txt",
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
        self.cpp_info.set_property("cmake_file_name", "metal-cpp")
        self.cpp_info.set_property("cmake_target_name", "metal-cpp::metal-cpp")
        self.cpp_info.set_property("pkg_config_name", "metal-cpp")
        self.cpp_info.bindirs = []
        self.cpp_info.frameworkdirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.resdirs = []

        self.cpp_info.frameworks = ["Foundation", "Metal", "MetalKit", "QuartzCore", "MetalFX"]
