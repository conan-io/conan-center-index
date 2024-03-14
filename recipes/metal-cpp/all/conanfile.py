from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
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

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"

    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "header_only": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "header_only": False,
    }

    @property
    def _min_cppstd(self):
        return 17

    def export_sources(self):
        copy(self, "CMakeLists.txt", src=self.recipe_folder, dst=self.export_sources_folder)
        copy(self, "implementation.cpp",
            src=os.path.join(self.recipe_folder, 'src'),
            dst=os.path.join(self.export_sources_folder, 'src'))

    def layout(self):
        if self.options.header_only:
            basic_layout(self, src_folder="src")
        else:
            cmake_layout(self, src_folder="src")

    def package_id(self):
        if self.info.options.header_only:
            self.info.clear()

    def configure(self):
        if self.options.header_only:
            self.options.rm_safe("fPIC")
            self.options.rm_safe("shared")
        elif self.options.shared:
            self.options.rm_safe("fPIC")

    def validate(self):
        if not is_apple_os(self):
            raise ConanInvalidConfiguration("Metal can only be used on an Apple OS.")

        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)

        minimum_os_version = None
        if self.version == '13':
            minimum_os_version = {'Macos': '13.0', 'iOS': '16.0'}
        elif self.version == '13.3':
            minimum_os_version = {'Macos': '13.3', 'iOS': '16.4'}
        elif self.version == '14':
            minimum_os_version = {'Macos': '14.0', 'iOS': '17.0'}
        elif self.version == '14.2':
            minimum_os_version = {'Macos': '14.2', 'iOS': '17.2'}

        os_name = str(self.settings.os)
        if not minimum_os_version or not os_name in minimum_os_version:
            raise ConanInvalidConfiguration("Missing minimum system version definitions.")
        elif self.settings.os.version < Version(minimum_os_version[os_name]):
            os_ver = self.settings.os.version
            req_os_ver = minimum_os_version[os_name]
            raise ConanInvalidConfiguration(f"metal-cpp {self.version} requires {os_name} version {req_os_ver} but {os_ver} is the target.")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        if not self.options.header_only:
            tc = CMakeToolchain(self)
            # The MetalFX component was added with the macOS 14 release of metal-cpp
            if self.version >= Version('14'):
                tc.variables["HAS_METALFX"] = True
            # Relocatable shared lib on Macos
            tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0042"] = "NEW"
            tc.generate()

    def build(self):
        if not self.options.header_only:
            cmake = CMake(self)
            cmake.configure(build_script_folder=self.export_sources_folder)
            cmake.build()

    def package(self):
        copy(
            self,
            pattern="LICENSE.txt",
            dst=os.path.join(self.package_folder, "licenses"),
            src=os.path.join(self.source_folder)
        )

        if not self.options.header_only:
            cmake = CMake(self)
            cmake.install()
        else:
            copy(
                self,
                pattern="**.hpp",
                dst=os.path.join(self.package_folder, "include"),
                src=os.path.join(self.source_folder),
                keep_path=True
            )

    def package_info(self):
        target = "metal-cpp-header-only" if self.options.header_only else "metal-cpp"
        self.cpp_info.set_property("cmake_file_name", "metal-cpp")
        self.cpp_info.set_property("cmake_target_name", f"metal-cpp::{target}")
        self.cpp_info.set_property("pkg_config_name",  "metal-cpp")

        if self.options.header_only:
            self.cpp_info.bindirs = []
            self.cpp_info.libs = []
            self.cpp_info.defines.append("METALCPP_HEADER_ONLY=1")
        else:
            self.cpp_info.bindirs = []
            self.cpp_info.libs = ["metal-cpp"]

        self.cpp_info.set_property("pkg_config_name", "metal-cpp")
        self.cpp_info.frameworks = ["Foundation", "Metal", "MetalKit", "QuartzCore"]
        if self.version >= Version('14'):
            self.cpp_info.frameworks.append("MetalFX")
