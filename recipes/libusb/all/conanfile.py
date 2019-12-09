from conans import ConanFile, AutoToolsBuildEnvironment, MSBuild, tools
import os

class LibUSBConan(ConanFile):
    name = "libusb"
    description = "A cross-platform library to access USB devices"
    license = "LGPL-2.1"
    homepage = "https://github.com/libusb/libusb"
    url = "https://github.com/conan-io/conan-center-index"
    topics = ("conan", "libusb", "usb", "device")
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "enable_udev": [True, False], "fPIC": [True, False]}
    default_options = {'shared': False, 'enable_udev': True, 'fPIC': True}
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

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_folder = self.name + "-" + self.version
        os.rename(extracted_folder, self._source_subfolder)

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def config_options(self):
        if self.settings.os != "Linux":
            del self.options.enable_udev
        if self.settings.os == "Windows":
            del self.options.fPIC

    def system_requirements(self):
        if self.settings.os == "Linux":
            if self.options.enable_udev:
                package_tool = tools.SystemPackageTool(conanfile=self)
                libudev_name = ""
                os_info = tools.OSInfo()
                if os_info.with_apt:
                    libudev_name = "libudev-dev"
                elif os_info.with_yum:
                    libudev_name = "libudev-devel"
                elif os_info.with_zypper:
                    libudev_name = "libudev-devel"
                elif os_info.with_pacman:
                    libudev_name = "libsystemd systemd"
                else:
                    self.output.warn("Could not install libudev: Undefined package name for current platform.")
                    return
                package_tool.install(packages=libudev_name, update=True)

    def _build_visual_studio(self):
        with tools.chdir(self._source_subfolder):
            solution_file = "libusb_2017.sln"
            if self.settings.compiler.version == "14":
                solution_file = "libusb_2015.sln"
            if self.settings.compiler.version == "12":
                solution_file = "libusb_2013.sln"
            elif self.settings.compiler.version == "11":
                solution_file = "libusb_2012.sln"
            solution_file = os.path.join("msvc", solution_file)
            platforms = {"x86":"Win32"}
            msbuild = MSBuild(self)
            msbuild.build(solution_file, platforms=platforms, upgrade_project=False)

    def _configure_autotools(self):
        if not self._autotools:
            self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
            configure_args = ['--enable-shared' if self.options.shared else '--disable-shared']
            configure_args.append('--enable-static' if not self.options.shared else '--disable-static')
            if self.settings.os == "Linux":
                configure_args.append('--enable-udev' if self.options.enable_udev else '--disable-udev')
            elif self._is_mingw:
                if self.settings.arch == "x86_64":
                    configure_args.append('--host=x86_64-w64-mingw32')
                elif self.settings.arch == "x86":
                    configure_args.append('--build=i686-w64-mingw32')
                    configure_args.append('--host=i686-w64-mingw32')
            self._autotools.configure(args=configure_args, configure_dir=self._source_subfolder)
        return self._autotools

    def build(self):
        if self._is_msvc:
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
            tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
            la_file = os.path.join(self.package_folder, "lib", "libusb-1.0.la")
            if os.path.isfile(la_file):
                os.remove(la_file)

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.includedirs.append(os.path.join("include", "libusb-1.0"))
        if self.settings.os == "Linux":
            self.cpp_info.system_libs.append("pthread")
            if self.options.enable_udev:
                self.cpp_info.system_libs.append("udev")
        elif self.settings.os == "Macos":
            self.cpp_info.system_libs = ["objc"]
            self.cpp_info.frameworks = ["IOKit", "CoreFoundation"]
