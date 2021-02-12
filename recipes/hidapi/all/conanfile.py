from conans import ConanFile, AutoToolsBuildEnvironment, MSBuild, tools
import os, glob

class HidapiConan(ConanFile):
    name = "hidapi"
    license = "BSD-Style"
    homepage = "https://github.com/libusb/hidapi"
    url = "https://github.com/conan-io/conan-center-index"
    topics = ("conan", "hidapi", "usb", "device","hid")
    description = "conan package for hidapi"
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "minosx": ['10.7', '10.8', '10.9', '10.10', '10.11'],
        "fPIC": [True, False],
        "with_libusb": [True, False],
        "shared": [True, False], 
        "enable_udev": [True, False]
    }
    default_options = {
        "minosx": 10.7, 
        "fPIC": True, 
        "with_libusb": False,
        "shared": True,
        "enable_udev": True
    }
    _autotools = None

    @property
    def _source_subfolder(self):
        return os.path.join(self.source_folder, "source_subfolder")        

    @property
    def _is_mingw(self):
        return self.settings.os == "Windows" and self.settings.compiler == "gcc"

    @property
    def _is_msvc(self):
        return self.settings.os == "Windows" and self.settings.compiler == "Visual Studio"

    def config_options(self):
        if self.settings.os != "Macos":
            del self.options.minosx
        if self.settings.os != "Linux":
            del self.options.with_libusb
        if self.settings.os == "Windows":
            del self.options.fPIC

    def requirements(self):
        if self.settings.os == "Linux" or self.settings.os == "FreeBSD":
            self.requires("libusb/[~=1.0]")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("{}-{}-{}".format(self.name,self.name, self.version), self._source_subfolder)

    def _configure_autotools(self):
        if not self._autotools:
            self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
            configure_args = ["--enable-shared" if self.options.shared else "--disable-shared"]
            configure_args.append("--enable-static" if not self.options.shared else "--disable-static")
            if self.settings.os == "Linux":
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
            self.build_msvc()
        else:
            self.build_unix()

    def build_msvc(self):
        msbuild = MSBuild(self)
        msbuild.build("%s/windows/hidapi.vcxproj" % self._source_subfolder,
                      platforms={'x86': 'x86','x86_64': 'x64'})

    

    def build_unix(self):
        self.run("cd %s && ./bootstrap" % self._source_subfolder)
        if self.settings.os == "Macos":
            configure = "%s/configure" % self._source_subfolder
            tools.replace_in_file(configure, r"-install_name \$rpath/",
                                  "-install_name ")
        autotools = AutoToolsBuildEnvironment(self)
        if self.settings.os == "Macos":
            autotools.flags.append('-mmacosx-version-min=%s' %
                                   self.options.minosx)

        autotools = self._configure_autotools()
        autotools.make()
        autotools.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "share"))
        la_files = {
            os.path.join(self.package_folder, "lib", "libhidapi-hidraw.la"),
            os.path.join(self.package_folder, "lib", "libhidapi-libusb.la"),
            os.path.join(self.package_folder, "lib", "libhidapi.la")
        }
        for la_file in la_files:
            if os.path.isfile(la_file):
                os.remove(la_file)

    def package(self):
        self.copy("LICENSE*.txt", src=self._source_subfolder, dst="licenses")
        self.copy("hidapi/*.h", dst="include", src=self._source_subfolder)
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
