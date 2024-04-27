import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import cmake_layout
from conan.tools.files import apply_conandata_patches, chdir, copy, export_conandata_patches, get, rmdir
from conan.tools.gnu import Autotools, AutotoolsDeps, AutotoolsToolchain

required_conan_version = ">=1.53.0"


class Openni2Conan(ConanFile):
    name = "openni2"
    description = "The OpenNI 2.0 API provides access to PrimeSense-compatible depth sensors"
    license = "Apache-2.0"
    homepage = "https://github.com/structureio/OpenNI2"
    url = "https://github.com/conan-io/conan-center-index"
    topics = ("rgb-d", "cameras", "driver", "computer-vision", "depth-sensor")

    package_type = "shared-library"
    settings = "os", "arch", "compiler", "build_type"

    def export_sources(self):
        export_conandata_patches(self)

    def package_id(self):
        if self.info.settings.build_type != "Debug":
            self.info.settings.build_type = "Release"

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("libjpeg/9e")
        if self.settings.os == "Linux":
            self.requires("libusb/1.0.26")
            self.requires("libudev/system")

    def validate(self):
        if self.settings.os != "Linux":
            # The library should also support Windows via MSBuild and macOS via Makefiles.
            raise ConanInvalidConfiguration("Only Linux builds are currently supported. Contributions are welcome!")
        if self.settings.arch not in ["x86", "x86_64", "armv6", "armv7"]:
            raise ConanInvalidConfiguration(f"{self.settings.arch} architecture is not supported.")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    @property
    def _build_type(self):
        return "Debug" if self.settings.build_type == "Debug" else "Release"

    @property
    def _platform(self):
        return {
            "x86": "x86",
            "x86_64": "x64",
            "armv6": "Armv6l",
            "armv7": "Arm",
        }[str(self.settings.arch)]


    def generate(self):
        tc = AutotoolsToolchain(self)
        tc.make_args.extend([
            f"CFG={self._build_type}",
            f"PLATFORM={self._platform}",
            # Disable -Werror
            "ALLOW_WARNINGS=1",
        ])
        tc.generate()
        deps = AutotoolsDeps(self)
        deps.generate()

    def build(self):
        apply_conandata_patches(self)
        rmdir(self, os.path.join(self.source_folder, "ThirdParty", "LibJPEG"))
        with chdir(self, self.source_folder):
            autotools = Autotools(self)
            autotools.make()

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        copy(self, "*", os.path.join(self.source_folder, "Include"), os.path.join(self.package_folder, "include", "openni2"))
        bin_dir = os.path.join(self.source_folder, "Bin", f"{self._platform}-{self._build_type}")
        copy(self, "*.a", bin_dir, os.path.join(self.package_folder, "lib"))
        copy(self, "*.so*", bin_dir, os.path.join(self.package_folder, "lib"))
        copy(self, "*.ini", os.path.join(self.source_folder, "Config"), os.path.join(self.package_folder, "res"))

    def package_info(self):
        # The component groupings are unofficial
        self.cpp_info.components["libopenni2"].libs = ["OpenNI2"]
        self.cpp_info.components["libopenni2"].includedirs.append(os.path.join("include", "openni2"))
        self.cpp_info.components["libopenni2"].requires = ["libjpeg::libjpeg"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["libopenni2"].system_libs.extend(["pthread", "m", "dl"])

        self.cpp_info.components["depthutils"].libs = ["DepthUtils"]
        self.cpp_info.components["depthutils"].includedirs.append(os.path.join("include", "openni2"))
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["depthutils"].system_libs.extend(["rt"])

        self.cpp_info.components["drivers"].libs = ["DummyDevice", "OniFile", "PS1080", "PSLink"]
        self.cpp_info.components["drivers"].includedirs.append(os.path.join("include", "openni2"))
        self.cpp_info.components["drivers"].libdirs.append(os.path.join("lib", "OpenNI2", "Drivers"))
        self.cpp_info.components["drivers"].resdirs = ["res"]
        self.cpp_info.components["drivers"].requires = ["libjpeg::libjpeg", "libusb::libusb", "libudev::libudev"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["drivers"].system_libs.extend(["pthread", "m", "dl"])
