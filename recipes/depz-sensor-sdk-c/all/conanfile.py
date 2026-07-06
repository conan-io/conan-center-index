import os

from conan import ConanFile
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get

required_conan_version = ">=2.0"


class DepzSensorSdkCConan(ConanFile):
    name = "depz-sensor-sdk-c"
    description = (
        "Contract-first C11 decode/codec SDK for the DEPZ USB sensor line "
        "(SR04, VL53L8CX/CH, BNO086): CRCs, packet framing, USB identity, "
        "firmware container parsing, and the per-sensor decode layer."
    )
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/depz-ai/depz-sensor-sdk"
    topics = ("sensors", "usb", "codec", "vl53l8", "bno086", "sr04", "embedded")
    package_type = "static-library"
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "fPIC": [True, False],
    }
    default_options = {
        "fPIC": True,
    }

    # The library lives in a subdirectory of the DEPZ monorepo tarball.
    _subfolder = "packages/depz-sensor-sdk-c"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        # Pure C library: no C++ standard library nor C++ ABI.
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        # Consumers never build the monorepo golden-vector test suite.
        tc.cache_variables["DEPZ_SENSOR_SDK_C_BUILD_TESTS"] = False
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure(build_script_folder=self._subfolder)
        cmake.build()

    def package(self):
        # The monorepo ships a single top-level MIT license file.
        copy(self, "LICENSE",
             src=os.path.join(self.source_folder, "packages", "depz-sensor-sdk-cpp"),
             dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["depz_sensor_sdk"]
        self.cpp_info.set_property("cmake_file_name", "depz-sensor-sdk-c")
        self.cpp_info.set_property("cmake_target_name", "depz::sensor_sdk_c")
        if self.settings.os in ("Linux", "FreeBSD"):
            self.cpp_info.system_libs = ["m"]
