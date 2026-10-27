import os

from conan import ConanFile
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir

required_conan_version = ">=2.0"


class DepzSensorSdkCConan(ConanFile):
    name = "depz-sensor-sdk-c"
    description = (
        "C11 SDK for the DEPZ USB sensor line (HC-SR04 ultrasonic, VL53Lx / "
        "VL53L4 / VL53L5 / VL53L7 / VL53L8 ToF, BNO055 / BNO08x IMU): packet "
        "framing and codecs, per-sensor decoding, serial-port I/O, device "
        "discovery and recording / replay."
    )
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/depz-ai/depz-sensor-sdk"
    topics = ("sensors", "usb", "serial", "tof", "imu", "vl53l8", "bno086", "sr04")
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
        # The C package ships its own MIT license file.
        copy(self, "LICENSE",
             src=os.path.join(self.source_folder, self._subfolder),
             dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        # The embedded ams TMF8829 sensor firmware is MIT: its licence goes with
        # ours; the CMake config files are Conan's to generate.
        copy(self, "LICENSES-MIT.TXT",
             src=os.path.join(self.source_folder, self._subfolder, "licenses", "tmf8829"),
             dst=os.path.join(self.package_folder, "licenses", "tmf8829"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.libs = ["depz_sensor_sdk_c"]
        self.cpp_info.set_property("cmake_file_name", "depz-sensor-sdk-c")
        self.cpp_info.set_property("cmake_target_name", "depz::sensor_sdk_c")
        # The serial-port layer: threads, plus the OS's port enumeration API.
        if self.settings.os in ("Linux", "FreeBSD"):
            self.cpp_info.system_libs = ["m", "pthread"]
        elif self.settings.os == "Windows":
            self.cpp_info.system_libs = ["setupapi", "cfgmgr32"]
        elif self.settings.os == "Macos":
            self.cpp_info.frameworks = ["IOKit", "CoreFoundation"]
