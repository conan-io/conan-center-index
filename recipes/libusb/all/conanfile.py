from conan import ConanFile
from conan.tools.microsoft import is_msvc, MSBuildDeps, MSBuildToolchain, MSBuild, VCVars
from conan.tools.files import get, rmdir, rm, copy, chdir, replace_in_file
from conan.tools.layout import basic_layout, vs_layout
from conan.tools.gnu import AutotoolsToolchain, PkgConfigDeps, AutotoolsDeps, Autotools
from conan.tools.env import VirtualBuildEnv
# TODO: Update when Conan 1.52.0 is available in CCI
from conans.tools import Version
from conans import tools
import os
import re

required_conan_version = ">=1.48.0"


class LibUSBConan(ConanFile):
    name = "libusb"
    description = "A cross-platform library to access USB devices"
    license = "LGPL-2.1"
    homepage = "https://github.com/libusb/libusb"
    url = "https://github.com/conan-io/conan-center-index"
    topics = ("usb", "device")
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "enable_udev": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "enable_udev": True,
    }

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _is_mingw(self):
        return self.settings.os == "Windows" and self.settings.compiler == "gcc"

    @property
    def _settings_build(self):
        return self.settings_build if hasattr(self, "settings_build") else self.settings

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if self.settings.os not in ["Linux", "Android"]:
            del self.options.enable_udev
        # FIXME: enable_udev should be True for Android, but libudev recipe is missing
        if self.settings.os == "Android":
            self.options.enable_udev = False

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        try:
            del self.settings.compiler.libcxx
        except Exception:
            pass
        try:
            del self.settings.compiler.cppstd
        except Exception:
            pass

    def build_requirements(self):
        if self._settings_build.os == "Windows" and not is_msvc(self) and not tools.get_env("CONAN_BASH_PATH"):
            self.tool_requires("msys2/cci.latest")

    def requirements(self):
        if self.settings.os == "Linux":
            if self.options.enable_udev:
                self.requires("libudev/system")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
                  destination=self.source_folder, strip_root=True)

    def layout(self):
        if is_msvc(self):
            vs_layout(self)
        else:
            basic_layout(self, src_folder="src")

    def generate(self):
        if is_msvc(self):
            tc = MSBuildToolchain(self)
            tc.generate()
            tc = MSBuildDeps(self)
            tc.generate()
            tc = VCVars(self)
            tc.generate()
        else:
            tc = AutotoolsToolchain(self)
            tc.configure_args.append("--enable-shared" if self.info.options.shared else "--disable-shared")
            tc.configure_args.append("--enable-static" if not self.options.shared else "--disable-static")
            if self.settings.os in ["Linux", "Android"]:
                tc.configure_args.append("--enable-udev" if self.options.enable_udev else "--disable-udev")
            elif self._is_mingw:
                if self.settings.arch == "x86_64":
                    tc.configure_args.append("--host=x86_64-w64-mingw32")
                elif self.settings.arch == "x86":
                    tc.configure_args.append("--build=i686-w64-mingw32")
                    tc.configure_args.append("--host=i686-w64-mingw32")
            tc.generate()
            tc = AutotoolsDeps(self)
            tc.generate()
            tc = PkgConfigDeps(self)
            tc.generate()
            ms = VirtualBuildEnv(self)
            ms.generate(scope="build")

    def _build_visual_studio(self):
        with chdir(self, self._source_subfolder):
            # Assume we're using the latest Visual Studio and default to libusb_2019.sln
            # (or libusb_2017.sln for libusb < 1.0.24).
            # If we're not using the latest Visual Studio, select an appropriate solution file.
            solution_msvc_year = 2019 if Version(self.version) >= "1.0.24" else 2017

            solution_msvc_year = {
                "11": 2012,
                "12": 2013,
                "14": 2015,
                "15": 2017
            }.get(str(self.settings.compiler.version), solution_msvc_year)

            solution_file = os.path.join("msvc", "libusb_{}.sln".format(solution_msvc_year))
            platforms = {"x86":"Win32"}
            properties = {
                # Enable LTO when CFLAGS contains -GL
                "WholeProgramOptimization": "true" if any(re.finditer("(^| )[/-]GL($| )", tools.get_env("CFLAGS", ""))) else "false",
            }
            msbuild = MSBuild(self)
            build_type = "Debug" if self.settings.build_type == "Debug" else "Release"
            msbuild.build(solution_file, platforms=platforms, upgrade_project=False, properties=properties, build_type=build_type)

    def build(self):
        if is_msvc(self):
            if Version(self.version) < "1.0.24":
                for vcxproj in ["fxload_2017", "getopt_2017", "hotplugtest_2017", "libusb_dll_2017",
                                "libusb_static_2017", "listdevs_2017", "stress_2017", "testlibusb_2017", "xusb_2017"]:
                    vcxproj_path = os.path.join(self._source_subfolder, "msvc", "%s.vcxproj" % vcxproj)
                    replace_in_file(self, vcxproj_path, "<WindowsTargetPlatformVersion>10.0.16299.0</WindowsTargetPlatformVersion>", "")
            with chdir(self, self._source_subfolder):
                # Assume we're using the latest Visual Studio and default to libusb_2019.sln
                # (or libusb_2017.sln for libusb < 1.0.24).
                # If we're not using the latest Visual Studio, select an appropriate solution file.
                solution_msvc_year = 2019 if Version(self.version) >= "1.0.24" else 2017

                solution_msvc_year = {
                    "11": 2012,
                    "12": 2013,
                    "14": 2015,
                    "15": 2017
                }.get(str(self.settings.compiler.version), solution_msvc_year)

                solution_file = os.path.join("msvc", "libusb_{}.sln".format(solution_msvc_year))
                platforms = {"x86":"Win32"}
                properties = {
                    # Enable LTO when CFLAGS contains -GL
                    "WholeProgramOptimization": "true" if any(re.finditer("(^| )[/-]GL($| )", tools.get_env("CFLAGS", ""))) else "false",
                }
                msbuild = MSBuild(self)
                build_type = "Debug" if self.settings.build_type == "Debug" else "Release"
                msbuild.build(solution_file, platforms=platforms, upgrade_project=False, properties=properties, build_type=build_type)
        else:
            autotools = Autotools(self)
            autotools.autoreconf()
            autotools.configure()
            autotools.make()

    def _package_visual_studio(self):
        self.copy(pattern="libusb.h", dst=os.path.join("include", "libusb-1.0"), src=os.path.join(self._source_subfolder, "libusb"), keep_path=False)
        arch = "x64" if self.settings.arch == "x86_64" else "Win32"
        build_type = "Debug" if self.settings.build_type == "Debug" else "Release"
        source_dir = os.path.join(self._source_subfolder, arch, build_type, "dll" if self.options.shared else "lib")
        if self.options.shared:
            copy(self, pattern="libusb-1.0.dll", dst=os.path.join(self.package_folder, "bin"), src=source_dir, keep_path=False)
            copy(self, pattern="libusb-1.0.lib", dst=os.path.join(self.package_folder, "lib"), src=source_dir, keep_path=False)
            copy(self, pattern="libusb-usbdk-1.0.dll", dst=os.path.join(self.package_folder, "bin"), src=source_dir, keep_path=False)
            copy(self, pattern="libusb-usbdk-1.0.lib", dst=os.path.join(self.package_folder, "lib"), src=source_dir, keep_path=False)
        else:
            copy(self, pattern="libusb-1.0.lib", dst=os.path.join(self.package_folder, "lib"), src=source_dir, keep_path=False)
            copy(self, pattern="libusb-usbdk-1.0.lib", dst=os.path.join(self.package_folder, "lib"), src=source_dir, keep_path=False)

    def package(self):
        copy(self, "COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        if is_msvc(self):
            self._package_visual_studio()
        else:
            autotools = Autotools(self)
            autotools.install()
            rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
            rm(self, "*.la", os.path.join(self.package_folder, "lib"))

    def package_info(self):
        self.cpp_info.names["pkg_config"] = "libusb-1.0"
        self.cpp_info.set_property("pkg_config_name", "libusb-1.0")
        self.cpp_info.libs = ["libusb-1.0"] if is_msvc(self) else ["usb-1.0"]
        self.cpp_info.includedirs.append(os.path.join("include", "libusb-1.0"))
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("pthread")
        elif self.settings.os == "Macos":
            self.cpp_info.system_libs = ["objc"]
            self.cpp_info.frameworks = ["IOKit", "CoreFoundation", "Security"]
        elif self.settings.os == "Windows":
            self.cpp_info.system_libs = ["advapi32"]
