import os

from conan import ConanFile
from conan.tools.cmake import cmake_layout
from conan.tools.env import Environment
from conan.tools.files import copy, get

required_conan_version = ">=2.4"


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
    languages = ["C"]

    def layout(self):
        cmake_layout(self, src_folder="src")

    def package_id(self):
        self.info.settings.clear()

    def build_requirements(self):
        self.tool_requires("cpython/[>=3.12 <4]")

    def source(self):
        info = self.conan_data["sources"][self.version]
        get(self, **info["mavlink"], strip_root=True)
        get(self, **info["pymavlink"], strip_root=True, destination="pymavlink")

    def generate(self):
        # To install pyelftools
        env = Environment()
        env.append_path("PYTHONPATH", self._site_packages_dir)
        env.append_path("PATH", os.path.join(self._site_packages_dir, "bin"))
        env.vars(self).save_script("pythonpath")

    @property
    def _site_packages_dir(self):
        return os.path.join(self.build_folder, "site-packages")

    def _pip_install(self, packages):
        self.run(f"python -m pip install {' '.join(packages)} --no-cache-dir --target={self._site_packages_dir}",
                 cwd=self.source_folder)

    def build(self):
        # Reproduce these CMake steps https://github.com/mavlink/mavlink/blob/5e3a42b8f3f53038f2779f9f69bd64767b913bb8/CMakeLists.txt#L32-L39
        # for a tighter control over the created temporary Python environment.
        self._pip_install(["-r", "pymavlink/requirements.txt"])
        self.run("python -m pymavlink.tools.mavgen --lang=C"
                 f" --wire-protocol={self.options.wire_protocol}"
                 f" --output {self.build_folder}/include/mavlink/"
                 f" message_definitions/v1.0/{self.options.dialect}.xml",
                 cwd=self.source_folder)

    def package(self):
        copy(self, "COPYING", self.source_folder, os.path.join(self.package_folder, "licenses"))
        copy(self, "*", os.path.join(self.build_folder, "include"), os.path.join(self.package_folder, "include"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "MAVLink")
        self.cpp_info.set_property("cmake_target_name", "MAVLink::mavlink")
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
