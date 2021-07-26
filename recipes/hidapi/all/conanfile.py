import os
from conans import ConanFile, AutoToolsBuildEnvironment, MSBuild, tools
from conans.errors import ConanInvalidConfiguration


class HidapiConan(ConanFile):
    name = "hidapi"
    description = "HIDAPI is a multi-platform library which allows an application to interface " \
                  "with USB and Bluetooth HID-Class devices on Windows, Linux, FreeBSD, and macOS."
    topics = ("libusb", "hid-class", "bluetooth")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/libusb/hidapi"
    license = "GPL-3-or-later", "BSD-3-Clause"
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "fPIC": [True, False],
        "shared": [True, False],
    }
    default_options = {
        "fPIC": True,
        "shared": False,
    }
    generators = "pkg_config"
    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if self.settings.compiler == "Visual Studio":
            self.options.shared = True

    def configure(self):
        if self.settings.compiler == "Visual Studio" and not self.options.shared:
            raise ConanInvalidConfiguration("Static libraries for Visual Studio are currently not available")
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)

    def build_requirements(self):
        if self.settings.compiler != "Visual Studio":
            self.build_requires("libtool/2.4.6")

    def requirements(self):
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.requires("libusb/1.0.24")

    def _patch_sources(self):
        tools.replace_in_file(os.path.join(self._source_subfolder, "configure.ac"),
                              "AC_CONFIG_MACRO_DIR", "dnl AC_CONFIG_MACRO_DIR")

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        with tools.chdir(self._source_subfolder):
            self.run("./bootstrap")
        if self.settings.os == "Macos":
            tools.replace_in_file(os.path.join(self._source_subfolder, "configure"),
                                  r"-install_name \$rpath/", "-install_name ")
        self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        args = ["--enable-shared" if self.options.shared else "--disable-shared",
                "--enable-static" if not self.options.shared else "--disable-static"]
        self._autotools.configure(configure_dir=self._source_subfolder, args=args)
        return self._autotools

    def build(self):
        self._patch_sources()
        if self.settings.compiler == "Visual Studio":
            self._build_msvc()
        else:
            autotools = self._configure_autotools()
            autotools.make()

    def _build_msvc(self):
        msbuild = MSBuild(self)
        msbuild.build(os.path.join(self._source_subfolder, "windows", "hidapi.sln"),
                      platforms={"x86": "Win32"})

    def package(self):
        self.copy("LICENSE*", src=self._source_subfolder, dst="licenses")
        if self.settings.os == "Windows":
            self.copy(os.path.join("hidapi", "*.h"), dst="include", src=self._source_subfolder)
            self.copy("*hidapi.lib", dst="lib", keep_path=False)
            self.copy("*.dll", dst="bin", keep_path=False)
        else:
            autotools = self._configure_autotools()
            autotools.install()
            tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
            tools.rmdir(os.path.join(self.package_folder, "share"))
            tools.remove_files_by_mask(os.path.join(self.package_folder, "lib"), "*.la")

    def package_info(self):
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["libusb"].names["pkg_config"] = "hidapi-libusb"
            self.cpp_info.components["libusb"].libs = ["hidapi-libusb"]
            self.cpp_info.components["libusb"].requires = ["libusb::libusb"]
            self.cpp_info.components["libusb"].system_libs = ["pthread", "dl", "rt"]

            self.cpp_info.components["hidraw"].names["pkg_config"] = "hidapi-hidraw"
            self.cpp_info.components["hidraw"].libs = ["hidapi-hidraw"]
            self.cpp_info.components["hidraw"].system_libs = ["pthread", "dl"]
        else:
            self.cpp_info.libs = ["hidapi"]
            if self.settings.os == "Macos":
                self.cpp_info.frameworks.extend(["IOKit", "CoreFoundation", "Appkit"])
