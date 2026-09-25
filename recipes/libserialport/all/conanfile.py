from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os, fix_apple_shared_install_name
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import copy, get, mkdir, replace_in_file, rm, rmdir
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc, MSBuild, MSBuildToolchain
import os

required_conan_version = ">=2"


class LibSerialPortConan(ConanFile):
    name = "libserialport"
    package_type = "library"
    description = "Minimal cross-platform serial port library in C"
    topics = ("serial", "rs232", "usb", "sigrok")
    license = "LGPL-3.0-or-later"
    homepage = "https://sigrok.org/wiki/libserialport"
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

    @property
    def _msbuild_configuration(self):
        return "Debug" if self.settings.build_type == "Debug" else "Release"

    @property
    def _msbuild_platform(self):
        return {"x86": "Win32", "x86_64": "x64"}.get(str(self.settings.arch))

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if is_msvc(self):
            # libserialport.h unconditionally uses __declspec(dllimport) with MSVC,
            # so only a DLL build is supported
            self.options.rm_safe("shared")
            self.package_type = "shared-library"
        if self.options.get_safe("shared"):
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def layout(self):
        basic_layout(self, src_folder="src")

    def validate(self):
        if is_msvc(self) and self._msbuild_platform is None:
            raise ConanInvalidConfiguration(f"{self.ref} MSVC build supports only x86 and x86_64 architectures")

    def build_requirements(self):
        if not is_msvc(self):
            self.tool_requires("libtool/2.4.7")
            if self.settings_build.os == "Windows":
                # MinGW builds with autotools need a bash shell
                self.win_bash = True
                if not self.conf.get("tools.microsoft.bash:path", check_type=str):
                    self.tool_requires("msys2/cci.latest")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        if is_msvc(self):
            tc = MSBuildToolchain(self)
            tc.configuration = self._msbuild_configuration
            tc.generate()
        else:
            env = VirtualBuildEnv(self)
            env.generate()
            tc = AutotoolsToolchain(self)
            tc.generate()

    def _patch_vcxproj(self):
        vcxproj = os.path.join(self.source_folder, "libserialport.vcxproj")
        replace_in_file(self, vcxproj, "<PlatformToolset>v142</PlatformToolset>",
                        f"<PlatformToolset>{MSBuildToolchain(self).toolset}</PlatformToolset>")
        replace_in_file(self, vcxproj, "<WholeProgramOptimization>true</WholeProgramOptimization>", "")

    def build(self):
        if is_msvc(self):
            self._patch_vcxproj()
            msbuild = MSBuild(self)
            msbuild.build_type = self._msbuild_configuration
            msbuild.platform = self._msbuild_platform
            msbuild.build(os.path.join(self.source_folder, "libserialport.vcxproj"))
        else:
            mkdir(self, os.path.join(self.source_folder, "autostuff"))
            autotools = Autotools(self)
            autotools.autoreconf()
            autotools.configure()
            autotools.make()

    def package(self):
        copy(self, "COPYING", self.source_folder, os.path.join(self.package_folder, "licenses"))
        if is_msvc(self):
            copy(self, "libserialport.h", self.source_folder, os.path.join(self.package_folder, "include"))
            copy(self, "*.lib", self.source_folder, os.path.join(self.package_folder, "lib"), keep_path=False)
            copy(self, "*.dll", self.source_folder, os.path.join(self.package_folder, "bin"), keep_path=False)
        else:
            autotools = Autotools(self)
            autotools.install()
            rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
            rm(self, "*.la", os.path.join(self.package_folder, "lib"))
            fix_apple_shared_install_name(self)

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "libserialport")
        self.cpp_info.libs = ["libserialport"] if is_msvc(self) else ["serialport"]

        if self.settings.os == "Windows":
            self.cpp_info.system_libs = ["setupapi"]
        elif self.settings.os == "FreeBSD":
            self.cpp_info.system_libs = ["usb"]
        elif is_apple_os(self):
            self.cpp_info.frameworks = ["IOKit", "CoreFoundation"]
