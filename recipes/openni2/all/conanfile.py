import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
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
    options = {
        "with_jpeg": ["libjpeg", "libjpeg-turbo", "mozjpeg"],
    }
    default_options = {
        "with_jpeg": "libjpeg",
    }

    def export_sources(self):
        export_conandata_patches(self)

    def package_id(self):
        if self.info.settings.build_type != "Debug":
            self.info.settings.build_type = "Release"

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if self.options.with_jpeg == "libjpeg":
            self.requires("libjpeg/9e")
        elif self.options.with_jpeg == "libjpeg-turbo":
            self.requires("libjpeg-turbo/3.0.2")
        elif self.options.with_jpeg == "mozjpeg":
            self.requires("mozjpeg/4.1.5")
        if self.settings.os == "Linux":
            self.requires("libusb/1.0.26")
            self.requires("libudev/system")

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, 11)
        if self.settings.os != "Linux":
            # The library should also support Windows via MSBuild and macOS via Makefiles.
            raise ConanInvalidConfiguration("Only Linux builds are currently supported. Contributions are welcome!")
        if self.settings.arch not in ["x86", "x86_64"] and not self.settings.arch.startswith("arm"):
            raise ConanInvalidConfiguration(f"{self.settings.arch} architecture is not supported.")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    @property
    def _build_type(self):
        return "Debug" if self.settings.build_type == "Debug" else "Release"

    @property
    def _platform(self):
        if self.settings.arch == "x86":
            return "x86"
        if self.settings.arch == "x86_64":
            return "x64"
        if self.settings.arch.startswith("arm"):
            return "Arm"

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
        copy(self, "*.so*", bin_dir, os.path.join(self.package_folder, "lib"))
        copy(self, "*.ini", os.path.join(self.source_folder, "Config"), os.path.join(self.package_folder, "res"))

    def package_info(self):
        # The CMake file and target names are unofficial since the project does not provide them,
        # but they match the name used in PCL, Pangolin and libfreenect2.
        self.cpp_info.set_property("cmake_file_name", "OpenNI2")
        self.cpp_info.set_property("cmake_target_name", "OpenNI2::OpenNI2")
        # Match the .pc file installed on Debian systems.
        self.cpp_info.set_property("pkg_config_name", "libopenni2")

        self.cpp_info.libs = ["OpenNI2"]
        self.cpp_info.includedirs.append(os.path.join("include", "openni2"))
        self.cpp_info.bindirs.append(os.path.join("lib", "OpenNI2", "Drivers"))
        self.cpp_info.resdirs = ["res"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["pthread", "m", "dl"])
