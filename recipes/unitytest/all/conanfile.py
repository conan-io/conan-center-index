from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rmdir, save
import os

required_conan_version = ">=1.53.0"


class UnityTestConan(ConanFile):
    name = "unitytest"
    description = "Unity Test is a unit testing framework built for C, with a focus on working with embedded toolchains"
    topics = ("unitytest", "unit-test", "tdd", "bdd")
    license = "BSL-1.0"
    homepage = "https://github.com/ThrowTheSwitch/Unity"
    url = "https://github.com/conan-io/conan-center-index"
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "fixture_extension": [True, False],
        "memory_extension": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "fixture_extension": True,
        "memory_extension": True,
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["UNITY_EXTENSION_FIXTURE"] = self.options.fixture_extension
        tc.cache_variables["UNITY_EXTENSION_MEMORY"] = self.options.memory_extension
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE.txt", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_find_mode", "both")
        self.cpp_info.set_property("cmake_file_name", "UnityTest")
        self.cpp_info.set_property("cmake_target_name", "UnityTest::UnityTest")
        self.cpp_info.libs = ["unity"]
        self.cpp_info.includedirs = ["include", "include/unity"]
