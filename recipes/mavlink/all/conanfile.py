import os

from conan import ConanFile
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir

required_conan_version = ">=2.0"


class MavlinkConan(ConanFile):
    name = "mavlink"
    description = "Marshalling / communication library for drones."
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/mavlink/mavlink"
    topics = ("mav", "drones", "marshalling", "communication")
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        # https://mavlink.io/en/messages/README.html
        "dialect": [
            "all",
            "common",
            "standard",
            "minimal",
            "development",
            "ardupilotmega",
            "ASLUAV",
            "AVSSUAS",
            "csAirLink",
            "cubepilot",
            "icarous",
            "loweheiser",
            "matrixpilot",
            "paparazzi",
            "storm32",
            "ualberta",
            "uAvionix",
        ],
        # https://github.com/ArduPilot/pymavlink/blob/v2.4.42/tools/mavgen.py#L24
        "wire_protocol": ["0.9", "1.0", "2.0"],
    }
    default_options = {
        "dialect": "common",
        "wire_protocol": "2.0",
    }

    def layout(self):
        cmake_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def build_requirements(self):
        self.tool_requires("cpython/[>=3.12 <4]")

    def source(self):
        info = self.conan_data["sources"][self.version]
        get(self, **info["mavlink"], strip_root=True)
        get(self, **info["pymavlink"], strip_root=True, destination="pymavlink")

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["MAVLINK_DIALECT"] = self.options.dialect
        tc.cache_variables["MAVLINK_VERSION"] = self.options.wire_protocol
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "COPYING", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "MAVLink")
        self.cpp_info.set_property("cmake_target_name", "MAVLink::mavlink")
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
