from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import cmake_layout
from conan.tools.files import copy, get
from conan.tools.scm import Version
import os


required_conan_version = ">=2.0"

class ClangConan(ConanFile):
    name = "vulkan-hpp"
    description = "C++ Bindings for Vulkan"
    license = "Apache-2"
    url = "https://github.com/entos-xe/conan-recipes"
    homepage = "https://github.com/KhronosGroup/Vulkan-Hpp"
    topics = "vulkan"
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        def sdk_version_number(version):
            if Version(version).micro is None:
                return f"{version}.0"
            return version

        self.requires(f"vulkan-headers/{sdk_version_number(self.version)}", transitive_headers=True)

    def package_id(self):
        self.info.clear()

    def validate(self):
        check_min_cppstd(self, 11)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        copy(self, "LICENSE.TXT", self.source_folder, os.path.join(self.package_folder, "licenses"))
        copy(self, "*", os.path.join(self.source_folder, "vulkan"), os.path.join(self.package_folder, "include", "vulkan"))

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
