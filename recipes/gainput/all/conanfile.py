from conan import ConanFile
from conan.tools.apple import is_apple_os
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get
import os

required_conan_version = ">=1.52.0"


class GainputConan(ConanFile):
    name = "gainput"
    description = "Cross-platform C++ input library supporting gamepads, keyboard, mouse, touch."
    license = "MIT"
    topics = ("gainput", "input", "keyboard", "gamepad", "mouse", "multi-touch")
    homepage = "https://gainput.johanneskuhlmann.de"
    url = "https://github.com/conan-io/conan-center-index"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            try:
                del self.options.fPIC
            except Exception:
                pass

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.requires("xorg/system")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["GAINPUT_SAMPLES"] = False
        tc.variables["GAINPUT_TESTS"] = False
        tc.variables["GAINPUT_BUILD_SHARED"] = self.options.shared
        tc.variables["GAINPUT_BUILD_STATIC"] = not self.options.shared
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        suffix = "{}{}".format("" if self.options.shared else "static",
                               "-d" if self.settings.build_type == "Debug" else "")
        self.cpp_info.libs = ["gainput" + suffix]
        if self.settings.os == "Windows":
            self.cpp_info.system_libs.extend(["xinput", "ws2_32"])
        elif self.settings.os == "Android":
            self.cpp_info.system_libs.extend(["native_app_glue", "log", "android"])
        elif is_apple_os(self):
            self.cpp_info.frameworks.extend(["CoreFoundation", "CoreGraphics", "Foundation", "IOKit", "GameController"])
            if self.settings.os == "iOS":
                self.cpp_info.frameworks.extend(["UIKit", "CoreMotion"])
            else:
                self.cpp_info.frameworks.append("AppKit")
