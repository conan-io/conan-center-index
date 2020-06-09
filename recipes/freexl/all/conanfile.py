import glob
import os

from conans import ConanFile, AutoToolsBuildEnvironment, VisualStudioBuildEnvironment, tools

class FreexlConan(ConanFile):
    name = "freexl"
    description = "FreeXL is an open source library to extract valid data " \
                  "from within an Excel (.xls) spreadsheet."
    license = ["MPL-1.0", "GPL-2.0-only", "LGPL-2.1-only"]
    topics = ("conan", "freexl", "excel", "xls")
    homepage = "https://www.gaia-gis.it/fossil/freexl/index"
    url = "https://github.com/conan-io/conan-center-index"
    exports_sources = "patches/**"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    _autotools= None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.cppstd
        del self.settings.compiler.libcxx

    def build_requirements(self):
        if self.settings.os == "Windows" and self.settings.compiler != "Visual Studio" and \
           "CONAN_BASH_PATH" not in os.environ and tools.os_info.detect_windows_subsystem() != "msys2":
            self.build_requires("msys2/20190524")

    def requirements(self):
        self.requires("libiconv/1.16")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename(self.name + "-" + self.version, self._source_subfolder)

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        if self.settings.compiler == "Visual Studio":
            self._build_msvc()
        else:
            autotools = self._configure_autotools()
            autotools.make()

    def _build_msvc(self):
        args = "freexl_i.lib FREEXL_EXPORT=-DDLL_EXPORT" if self.options.shared else "freexl.lib"
        with tools.chdir(self._source_subfolder):
            with tools.vcvars(self.settings):
                with tools.environment_append(VisualStudioBuildEnvironment(self).vars):
                    self.run("nmake -f makefile.vc {}".format(args))

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        args = ["--disable-static" if self.options.shared else "--enable-static",
                "--enable-shared" if self.options.shared else "--disable-shared"]
        self._autotools.configure(args=args, configure_dir=self._source_subfolder)
        return self._autotools

    def package(self):
        self.copy("COPYING", dst="licenses", src=self._source_subfolder)
        if self.settings.compiler == "Visual Studio":
            self.copy("freexl.h", dst="include", src=os.path.join(self._source_subfolder, "headers"))
            self.copy("*.lib", dst="lib", src=self._source_subfolder)
            self.copy("*.dll", dst="bin", src=self._source_subfolder)
        else:
            autotools = self._configure_autotools()
            autotools.install()
            tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
            for la_file in glob.glob(os.path.join(self.package_folder, "lib", "*.la")):
                os.remove(la_file)

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os == "Linux":
            self.cpp_info.system_libs.append("m")
