import os

from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get

required_conan_version = ">=2.0"


class DepzSensorSdkCppConan(ConanFile):
    name = "depz-sensor-sdk-cpp"
    description = (
        "C++17 decode-layer SDK for the DEPZ USB sensor line: framed-protocol "
        "parser and per-sensor wire codecs (SR04, VL53L8CX/CH, BNO086). "
        "Pure codecs, no I/O."
    )
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/depz-ai/depz-sensor-sdk"
    topics = ("sensors", "usb", "decode", "protocol", "vl53l8", "bno086", "sr04")
    package_type = "static-library"
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "fPIC": [True, False],
    }
    default_options = {
        "fPIC": True,
    }

    # The library lives in a subdirectory of the DEPZ monorepo tarball.
    _subfolder = "packages/depz-sensor-sdk-cpp"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def validate(self):
        check_min_cppstd(self, 17)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        # Consumers never build the monorepo golden-vector test suite.
        tc.cache_variables["DEPZ_SENSOR_SDK_CPP_BUILD_TESTS"] = False
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure(build_script_folder=self._subfolder)
        cmake.build()

    def package(self):
        copy(self, "LICENSE",
             src=os.path.join(self.source_folder, self._subfolder),
             dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["depz_sensor_sdk"]
        self.cpp_info.set_property("cmake_file_name", "depz-sensor-sdk-cpp")
        self.cpp_info.set_property("cmake_target_name", "depz::sensor_sdk_cpp")
        self.cpp_info.set_property("cmake_target_aliases", ["depz::sensor_sdk"])
