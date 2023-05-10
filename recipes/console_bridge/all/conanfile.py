import os

from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rm

required_conan_version = ">=1.53.0"


class PackageConan(ConanFile):
    name = "console_bridge"
    description = "A ROS-independent library for logging that seamlessly pipes into rosconsole/rosout for ROS-dependent packages"
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/ros/console_bridge"
    topics = ("logging", "ros", "robotics")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    @property
    def _min_cppstd(self):
        return 14

    @property
    def _tests_enabled(self):
        return not self.conf.get("tools.build:skip_test", default=True, check_type=bool)

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        pass

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)

    def build_requirements(self):
        if self._tests_enabled:
            self.build_requires("gtest/1.13.0")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_TESTING"] = self._tests_enabled
        tc.generate()
        CMakeDeps(self).generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()
        if self._tests_enabled:
            cmake.test()

    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()

        rm(self, "*.pdb", os.path.join(self.package_folder))

    def package_info(self):
        self.cpp_info.libs = ["console_bridge"]

        self.cpp_info.set_property("cmake_module_file_name", "console_bridge")
        self.cpp_info.set_property("cmake_module_target_name", "console_bridge::console_bridge")
        self.cpp_info.set_property("cmake_file_name", "console_bridge")
        self.cpp_info.set_property("cmake_target_name", "console_bridge::console_bridge")
        self.cpp_info.set_property("pkg_config_name", "console_bridge")

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["m"]
