from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import get, copy
import os

required_conan_version = ">=2"


class BemanTransformViewConan(ConanFile):
    name = "beman-transform_view"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/elvisdukaj/transform_view"
    license = "Apache-2.0"
    package_type = "library"
    description = "A conditionally borrowed std::ranges::transform_view"
    topics = ("algorithm", "ranges")
    settings = "os", "arch", "compiler", "build_type"

    options = {
        "header_only": [True, False],
        "shared": [True, False],
    }
    default_options = {
        "header_only": True,
        "shared": False,
    }

    def validate(self):
        check_min_cppstd(self, "23")

    def layout(self):
        cmake_layout(self)

    def configure(self):
        if self.options.header_only:
            self.options.rm_safe("shared")

    def package_id(self):
        if self.info.options.header_only:
            self.info.clear()

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        if not self.options.header_only:
            tc = CMakeToolchain(self)
            tc.variables["BEMAN_TRANSFORM_VIEW_BUILD_TESTS"] = False
            tc.variables["BEMAN_TRANSFORM_VIEW_BUILD_EXAMPLES"] = False
            tc.generate()

    def build(self):
        if not self.options.header_only:
            cmake = CMake(self)
            cmake.configure()
            cmake.build()

    def package(self):
        copy(self, "LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)

        if self.options.header_only:
            copy(self, "*", dst=os.path.join(self.package_folder, "include"),
                 src=os.path.join(self.source_folder, "include"))
        else:
            cmake = CMake(self)
            cmake.install()

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "beman.transform_view")
        self.cpp_info.set_property("pkg_config_name", "beman.transform_view")
        self.cpp_info.set_property("cmake_target_name", "beman::transform_view")

        if self.options.header_only:
            self.cpp_info.bindirs = []
            self.cpp_info.libdirs = []
        else:
            self.cpp_info.libs = ["beman.transform_view"]
