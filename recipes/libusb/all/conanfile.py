from conan import ConanFile
from conan.tools import files
from conans import AutoToolsBuildEnvironment, MSBuild, tools
import os
import re

required_conan_version = ">=1.33.0"


class LibUSBConan(ConanFile):
    name = "libusb"
    description = "A cross-platform library to access USB devices"
    license = "LGPL-2.1"
    homepage = "https://github.com/libusb/libusb"
    url = "https://github.com/conan-io/conan-center-index"
    topics = ("conan", "libusb", "usb", "device")
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
    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _is_mingw(self):
        return self.settings.os == "Windows" and self.settings.compiler == "gcc"

    @property
    def _is_msvc(self):
        return self.settings.os == "Windows" and self.settings.compiler == "Visual Studio"

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
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def build_requirements(self):
        if self._settings_build.os == "Windows" and not self._is_msvc and not tools.get_env("CONAN_BASH_PATH"):
            self.build_requires("msys2/cci.latest")

    def requirements(self):
        if self.settings.os == "Linux":
            if self.options.enable_udev:
                self.requires("libudev/system")

    def source(self):
        files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _build_visual_studio(self):
        with tools.chdir(self._source_subfolder):
            # Assume we're using the latest Visual Studio and default to libusb_2019.sln
            # (or libusb_2017.sln for libusb < 1.0.24).
            # If we're not using the latest Visual Studio, select an appropriate solution file.
            solution_msvc_year = 2019 if tools.Version(self.version) >= "1.0.24" else 2017

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

    def _configure_autotools(self):
        if not self._autotools:
            self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
            configure_args = ["--enable-shared" if self.options.shared else "--disable-shared"]
            configure_args.append("--enable-static" if not self.options.shared else "--disable-static")
            if self.settings.os in ["Linux", "Android"]:
                configure_args.append("--enable-udev" if self.options.enable_udev else "--disable-udev")
            elif self._is_mingw:
                if self.settings.arch == "x86_64":
                    configure_args.append("--host=x86_64-w64-mingw32")
                elif self.settings.arch == "x86":
                    configure_args.append("--build=i686-w64-mingw32")
                    configure_args.append("--host=i686-w64-mingw32")
            self._autotools.configure(args=configure_args, configure_dir=self._source_subfolder)
        return self._autotools

    def build(self):
        if self._is_msvc:
            if tools.Version(self.version) < "1.0.24":
                for vcxproj in ["fxload_2017", "getopt_2017", "hotplugtest_2017", "libusb_dll_2017",
                                "libusb_static_2017", "listdevs_2017", "stress_2017", "testlibusb_2017", "xusb_2017"]:
                    vcxproj_path = os.path.join(self._source_subfolder, "msvc", "%s.vcxproj" % vcxproj)
                    tools.replace_in_file(vcxproj_path, "<WindowsTargetPlatformVersion>10.0.16299.0</WindowsTargetPlatformVersion>", "")
            self._build_visual_studio()
        else:
            autotools = self._configure_autotools()
            autotools.make()

    def _package_visual_studio(self):
        self.copy(pattern="libusb.h", dst=os.path.join("include", "libusb-1.0"), src=os.path.join(self._source_subfolder, "libusb"), keep_path=False)
        arch = "x64" if self.settings.arch == "x86_64" else "Win32"
        source_dir = os.path.join(self._source_subfolder, arch, str(self.settings.build_type), "dll" if self.options.shared else "lib")
        if self.options.shared:
            self.copy(pattern="libusb-1.0.dll", dst="bin", src=source_dir, keep_path=False)
            self.copy(pattern="libusb-1.0.lib", dst="lib", src=source_dir, keep_path=False)
            self.copy(pattern="libusb-usbdk-1.0.dll", dst="bin", src=source_dir, keep_path=False)
            self.copy(pattern="libusb-usbdk-1.0.lib", dst="lib", src=source_dir, keep_path=False)
        else:
            self.copy(pattern="libusb-1.0.lib", dst="lib", src=source_dir, keep_path=False)
            self.copy(pattern="libusb-usbdk-1.0.lib", dst="lib", src=source_dir, keep_path=False)

    def package(self):
        self.copy("COPYING", src=self._source_subfolder, dst="licenses", keep_path=False)
        if self._is_msvc:
            self._package_visual_studio()
        else:
            autotools = self._configure_autotools()
            autotools.install()
            files.rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
            tools.remove_files_by_mask(os.path.join(self.package_folder, "lib"), "*.la")

    def package_info(self):
        self.cpp_info.names["pkg_config"] = "libusb-1.0"
        self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.includedirs.append(os.path.join("include", "libusb-1.0"))
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("pthread")
        elif self.settings.os == "Macos":
            self.cpp_info.system_libs = ["objc"]
            self.cpp_info.frameworks = ["IOKit", "CoreFoundation", "Security"]
        elif self.settings.os == "Windows":
            self.cpp_info.system_libs = ["advapi32"]
