from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import copy, get, replace_in_file, rm, rmdir
from conan.tools.gnu import Autotools, AutotoolsToolchain, PkgConfigDeps
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc, MSBuild, MSBuildToolchain
from conan.tools.scm import Version
import os

required_conan_version = ">=1.54.0"


class HidapiConan(ConanFile):
    name = "hidapi"
    description = "HIDAPI is a multi-platform library which allows an application to interface " \
                  "with USB and Bluetooth HID-Class devices on Windows, Linux, FreeBSD, and macOS."
    topics = ("libusb", "hid-class", "bluetooth")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/libusb/hidapi"
    license = "GPL-3-or-later", "BSD-3-Clause"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "fPIC": [True, False],
        "shared": [True, False],
    }
    default_options = {
        "fPIC": True,
        "shared": False,
    }

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    @property
    def _msbuild_configuration(self):
        return "Debug" if self.settings.build_type == "Debug" else "Release"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if is_msvc(self):
            self.options.shared = True

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.requires("libusb/1.0.26")

    def validate(self):
        if is_msvc(self) and not self.options.shared:
            raise ConanInvalidConfiguration("Static libraries for Visual Studio are currently not available")

    def build_requirements(self):
        if not is_msvc(self):
            self.tool_requires("libtool/2.4.7")
            if self.settings.os in ["Linux", "FreeBSD"] and not self.conf.get("tools.gnu:pkg_config", check_type=str):
                self.tool_requires("pkgconf/1.9.3")
            if self._settings_build.os == "Windows":
                self.win_bash = True
                if not self.conf.get("tools.microsoft.bash:path", check_type=str):
                    self.tool_requires("msys2/cci.latest")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        if is_msvc(self):
            tc = MSBuildToolchain(self)
            tc.configuration = self._msbuild_configuration
            tc.properties["WholeProgramOptimization"] = "false"
            tc.generate()
        else:
            env = VirtualBuildEnv(self)
            env.generate()
            tc = AutotoolsToolchain(self)
            tc.generate()
            deps = PkgConfigDeps(self)
            deps.generate()

    def _patch_sources(self):
        replace_in_file(self, os.path.join(self.source_folder, "configure.ac"),
                        "AC_CONFIG_MACRO_DIR", "dnl AC_CONFIG_MACRO_DIR")

    def build(self):
        self._patch_sources()
        if is_msvc(self):
            # TODO: to remove once https://github.com/conan-io/conan/pull/12817 available in conan client
            replace_in_file(
                self, os.path.join(self.source_folder, "windows", "hidapi.vcxproj"),
                "<WholeProgramOptimization>true</WholeProgramOptimization>",
                "",
            )
            conantoolchain_props = os.path.join(self.generators_folder, MSBuildToolchain.filename)
            replace_in_file(
                self, os.path.join(self.source_folder, "windows", "hidapi.vcxproj"),
                "<Import Project=\"$(VCTargetsPath)\\Microsoft.Cpp.targets\" />",
                f"<Import Project=\"{conantoolchain_props}\" /><Import Project=\"$(VCTargetsPath)\\Microsoft.Cpp.targets\" />",
            )

            msbuild = MSBuild(self)
            msbuild.build_type = self._msbuild_configuration
            msbuild.platform = "Win32" if self.settings.arch == "x86" else msbuild.platform
            msbuild.build(os.path.join(self.source_folder, "windows", "hidapi.sln"), targets=["hidapi"])
        else:
            autotools = Autotools(self)
            autotools.autoreconf()
            autotools.configure()
            autotools.make()

    def package(self):
        copy(self, "LICENSE*", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        if is_msvc(self):
            copy(self, os.path.join("hidapi", "*.h"), src=self.source_folder, dst=os.path.join(self.package_folder, "include"))
            output_folder = os.path.join(self.source_folder, "windows")
            copy(self, "*hidapi.lib", src=output_folder, dst=os.path.join(self.package_folder, "lib"), keep_path=False)
            copy(self, "*.dll", src=output_folder, dst=os.path.join(self.package_folder, "bin"), keep_path=False)
        else:
            autotools = Autotools(self)
            autotools.install()
            rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
            rmdir(self, os.path.join(self.package_folder, "share"))
            rm(self, "*.la", os.path.join(self.package_folder, "lib"))
            fix_apple_shared_install_name(self)

    def package_info(self):
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["libusb"].set_property("pkg_config_name", "hidapi-libusb")
            self.cpp_info.components["libusb"].libs = ["hidapi-libusb"]
            self.cpp_info.components["libusb"].requires = ["libusb::libusb"]
            self.cpp_info.components["libusb"].system_libs = ["pthread", "dl", "rt"]

            self.cpp_info.components["hidraw"].set_property("pkg_config_name", "hidapi-hidraw")
            self.cpp_info.components["hidraw"].libs = ["hidapi-hidraw"]
            self.cpp_info.components["hidraw"].system_libs = ["pthread", "dl"]
        else:
            self.cpp_info.libs = ["hidapi"]
            if self.settings.os == "Macos":
                self.cpp_info.frameworks.extend(["IOKit", "CoreFoundation", "AppKit"])
            if Version(self.version) == "0.10.1" and self.settings.os == "Windows":
                self.cpp_info.system_libs = ["setupapi"]
