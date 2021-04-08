# Known Issues
#
# * Not support x64 for Windows
#
#     [libusb/hidapi](https://github.com/libusb/hidapi) provides a `sln` file to build for Windows, which lack support x64.
#
# If you get an idea to solve one of this issues, please report here or fork.
import os
from conans import ConanFile, AutoToolsBuildEnvironment, MSBuild, tools


class HidapiConan(ConanFile):
    name = "hidapi"
    description = "HIDAPI is a multi-platform library which allows an application to interface with USB and Bluetooth HID-Class devices on Windows, Linux, FreeBSD, and macOS."
    topics = ("conan", "hidapi", "libusb")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/libusb/hidapi"
    license = "BSD-Style"
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "minosx": ['10.7', '10.8', '10.9', '10.10', '10.11', '10.12', '10.13', '10.14', '10.15', '11'],
        "fPIC": [True, False],
        "with_libusb": [True, False]
    }
    default_options = {
        "minosx": 10.7, "fPIC": True, "with_libusb": False
    }
    generators = "pkg_config"

    @property
    def _source_dir(self):
        return "hidapi-hidapi-" + self.version

    def config_options(self):
        if self.settings.os != "Macos":
            del self.options.minosx
        if self.settings.os != "Linux":
            del self.options.with_libusb
        if self.settings.os == "Windows":
            self.settings.arch.remove("x86_64")

    def requirements(self):
        if self.settings.os == "Linux" or self.settings.os == "FreeBSD":
            self.requires("libusb/[~=1.0]")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        if self.settings.os != "Windows":
            self.run("chmod +x ./%s/bootstrap" % self._source_dir)

    def build(self):
        if self.settings.os == "Windows":
            if self.settings.compiler == "Visual Studio":
                self.build_msvc()
        else:
            self.build_unix()

    def build_msvc(self):
        msbuild = MSBuild(self)
        msbuild.build("%s/windows/hidapi.sln" % self._source_dir,
                      platforms={"x86": "Win32"})

    def build_unix(self):
        self.run(os.path.join(".", "bootstrap"), cwd=self._source_dir)
        if self.settings.os == "Macos":
            configure = os.path.join(self._source_dir, "configure")
            tools.replace_in_file(configure, r"-install_name \$rpath/",
                                  "-install_name ")
        autotools = AutoToolsBuildEnvironment(self)
        if self.settings.os == "Macos":
            autotools.flags.append('-mmacosx-version-min=%s' %
                                   self.options.minosx)

        autotools.configure(self._source_dir)
        autotools.make()

    def package(self):
        self.copy("LICENSE*.txt", src=self._source_dir, dst="licenses")
        self.copy(os.path.join("hidapi", "*.h"), dst="include", src=self._source_dir)
        self.copy("*hidapi.lib", dst="lib", keep_path=False)
        self.copy("*.dll", dst="bin", keep_path=False)
        self.copy("*.so", dst="lib", keep_path=False)
        self.copy("*.dylib", dst="lib", keep_path=False)
        self.copy("*.a", dst="lib", keep_path=False)

    def package_info(self):
        if self.settings.os == "Linux":
            if self.options.with_libusb:
                self.cpp_info.libs = ["hidapi-libusb"]
            else:
                self.cpp_info.libs = ["hidapi-hidraw"]
        else:
            self.cpp_info.libs = ["hidapi"]
