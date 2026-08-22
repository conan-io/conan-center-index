from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import XCRun
from conan.tools.build import check_min_cppstd
from conan.tools.files import get, copy
from conan.tools.layout import basic_layout
from conan.tools.scm import Version

import os
import platform

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

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def validate(self):
        os_name = str(self.settings.os)
        if not os_name in ["Macos", "iOS", "tvOS"]:
            raise ConanInvalidConfiguration("Metal can only be used on an Macos, iOS or tvOS platform.")

        if self.settings.compiler.get_safe("cppstd"):
            min_cppstd = "17"
            check_min_cppstd(self, min_cppstd)

        minimum_os_version = self.conan_data["minimum_os_version"][self.version][os_name]

        xcrun = XCRun(self)
        os_version = self.settings.get_safe("os.version")
        sdk_version = self.settings.get_safe("os.sdk_version")
        visible_sdk_version = xcrun.sdk_version if platform.system() == "Darwin" else None

        sdk_version = sdk_version or os_version or visible_sdk_version

        if sdk_version is None:
            # Will raise when `os.version` or `os.sdk_version` are not defined
            # and we are *NOT* running this on macOS
            raise ConanInvalidConfiguration(f"metal-cpp {self.version} requires the os.version or sdk.version settings, but the are not defined")

        if sdk_version < Version(minimum_os_version):
            raise ConanInvalidConfiguration(f"metal-cpp {self.version} requires {os_name} SDK version {minimum_os_version} but {sdk_version} is the target.")

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

        self.cpp_info.frameworks = ["Foundation", "Metal", "MetalKit", "QuartzCore"]
        if self.version >= Version('14'):
            self.cpp_info.frameworks.append("MetalFX")
