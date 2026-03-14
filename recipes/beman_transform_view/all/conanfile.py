from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout, CMakeDeps
from conan.tools.files import get, copy
import os

required_conan_version = ">=2"


class BemanTransformViewConan(ConanFile):
    name = "beman-transform_view"
    package_type = "static-library"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/elvisdukaj/transform_view"
    license = "Apache-2.0"
    description = ("A conditionally borrowed std::ranges::transform_view",)
    topics = ("algorithm", "ranges")
    settings = "os", "arch", "compiler", "build_type"

    def validate(self):
        if not self.settings.compiler.get_safe("cppstd"):
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++23. Please set compiler.cppstd=23 in your profile."
            )
        check_min_cppstd(self, "23")

    def layout(self):
        cmake_layout(self)

    def package_id(self):
        self.info.clear()

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        deps = CMakeDeps(self)
        deps.generate()

        tc = CMakeToolchain(self)
        tc.variables["BEMAN_TRANSFORM_VIEW_BUILD_TESTS"] = False
        tc.variables["BEMAN_TRANSFORM_VIEW_BUILD_EXAMPLES"] = False
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "beman.transform_view")
        self.cpp_info.set_property("pkg_config_name", "beman.transform_view")
        self.cpp_info.set_property("cmake_target_name", "beman::transform_view")

        self.cpp_info.libs = ["beman.transform_view"]
