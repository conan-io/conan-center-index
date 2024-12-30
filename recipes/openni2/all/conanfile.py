import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os, fix_apple_shared_install_name
from conan.tools.build import check_min_cppstd, cross_building
from conan.tools.cmake import cmake_layout
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import apply_conandata_patches, chdir, copy, export_conandata_patches, get, rmdir, replace_in_file
from conan.tools.gnu import Autotools, AutotoolsDeps, AutotoolsToolchain
from conan.tools.microsoft import is_msvc

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
            self.requires("libudev/255.13")
        if self.settings.os != "Windows":
            self.requires("libusb/1.0.26")

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, 11)
        if self.settings.os != "Linux" and not is_apple_os(self):
            # The library should also support Windows via MSBuild.
            raise ConanInvalidConfiguration("Only Linux and macOS builds are currently supported. Contributions are welcome!")
        if self.settings.arch not in ["x86", "x86_64"] and not str(self.settings.arch).startswith("arm"):
            raise ConanInvalidConfiguration(f"{self.settings.arch} architecture is not supported.")
        if cross_building(self) and is_apple_os(self):
            raise ConanInvalidConfiguration("Cross-building on Apple OS-s is not supported.")

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
        if str(self.settings.arch).startswith("arm"):
            return "Arm"

    @property
    def _default_compiler(self):
        if self.settings.compiler == "gcc":
            return "g++"
        elif self.settings.compiler in ["clang", "apple-clang"]:
            return "clang++"
        elif is_msvc(self):
            return "cl.exe"
        return None

    @property
    def _cxx(self):
        compilers_from_conf = self.conf.get("tools.build:compiler_executables", default={}, check_type=dict)
        buildenv_vars = VirtualBuildEnv(self).vars()
        return compilers_from_conf.get("cpp", buildenv_vars.get("CXX", self._default_compiler))

    def generate(self):
        tc = AutotoolsToolchain(self)
        tc.make_args.extend([
            f"CFG={self._build_type}",
            # For cross-compilation
            f"PLATFORM={self._platform}",
            f"{self._platform.upper()}_CXX={self._cxx}",
            f"{self._platform.upper()}_STAGING={self.build_folder}",
            # Disable -Werror
            "ALLOW_WARNINGS=1",
        ])
        tc.generate()
        deps = AutotoolsDeps(self)
        deps.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)
        rmdir(self, os.path.join(self.source_folder, "ThirdParty", "LibJPEG"))
        replace_in_file(self, os.path.join(self.source_folder, "Source", "Drivers", "PS1080", "Sensor", "Bayer.cpp"), "register ", "")
        if is_apple_os(self):
            for makefile in self.source_path.joinpath("Source", "Drivers").rglob("Makefile"):
                replace_in_file(self, makefile, "usb-1.0.0", "usb-1.0", strict=False)

    def build(self):
        self._patch_sources()
        with chdir(self, self.source_folder):
            autotools = Autotools(self)
            autotools.make()

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        copy(self, "*", os.path.join(self.source_folder, "Include"), os.path.join(self.package_folder, "include", "openni2"))
        bin_dir = os.path.join(self.source_folder, "Bin", f"{self._platform}-{self._build_type}")
        copy(self, "*.so*", bin_dir, os.path.join(self.package_folder, "lib"))
        copy(self, "*.dylib", bin_dir, os.path.join(self.package_folder, "lib"))
        copy(self, "*.ini", os.path.join(self.source_folder, "Config"), os.path.join(self.package_folder, "res"))
        fix_apple_shared_install_name(self)

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
            self.cpp_info.system_libs.extend(["pthread", "m", "dl", "rt"])
        elif is_apple_os(self):
            self.cpp_info.frameworks.extend(["CoreFoundation", "IOKit"])
