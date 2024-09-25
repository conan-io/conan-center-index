import os
from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import get, copy
from conan.tools.scm import Version

required_conan_version = ">=1.53.0"

class WiringpiConan(ConanFile):
    name = "wiringpi"
    description = "GPIO Interface library for the Raspberry Pi"
    license = "LGPL-3.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/WiringPi/WiringPi"
    topics = ("wiringpi", "gpio", "raspberrypi")
    settings = "os", "arch", "compiler", "build_type"
    package_type = "library"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "wpi_extensions": [True, False],
        "with_devlib": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "wpi_extensions": False,
        "with_devlib": True,
    }

    def export_sources(self):
        copy(self, "CMakeLists.txt", self.recipe_folder, self.export_sources_folder)

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if  Version(self.version) >= "3.2":
            self.requires("linux-headers-generic/6.5.9", transitive_headers=True)

    def validate(self):
        if self.settings.os != "Linux":
            raise ConanInvalidConfiguration(f"{self.ref} only works for Linux")
        if Version(self.version) >= 3.0:
            if self.settings.compiler == "gcc" and \
                Version(self.settings.compiler.version) < 8:
                raise ConanInvalidConfiguration(f"{self.ref} requires gcc >= 8")
            # wiringPi.c:1755:9: error: case label does not reduce to an integer constant
            if self.settings.compiler == "gcc" and \
                Version(self.settings.compiler.version).major == 11 and \
                self.settings.build_type == "Debug":
                raise ConanInvalidConfiguration(f"{self.ref} doesn't support gcc 11 in Debug build")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["WIRINGPI_SRC_DIR"] = self.source_folder.replace("\\", "/")
        tc.variables["WIRINGPI_WITH_WPI_EXTENSIONS"] = self.options.wpi_extensions
        tc.variables["WIRINGPI_WITH_DEV_LIB"] = self.options.with_devlib
        if  Version(self.version) >= "3.2":
            tc.variables["WIRINGPI_LINUX_HEADERS_DIR"] = self.dependencies["linux-headers-generic"].cpp_info.includedirs[0]
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure(build_script_folder=os.path.join(self.source_folder, os.pardir))
        cmake.build()

    def package(self):
        copy(self, pattern="COPYING*", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["wiringPi"]
        if self.options.with_devlib:
            self.cpp_info.libs.append("wiringPiDevLib")
        if self.options.wpi_extensions:
            self.cpp_info.libs.append("crypt")
        if self.settings.os == "Linux":
            self.cpp_info.system_libs = ["pthread", "m", "rt"]
