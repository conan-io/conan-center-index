import glob
import os

from conans import AutoToolsBuildEnvironment, ConanFile, tools
from conans.errors import ConanInvalidConfiguration


class LibbacktraceConan(ConanFile):
    name = "libbacktrace"
    description = "A C library that may be linked into a C/C++ program to produce symbolic backtraces."
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/ianlancetaylor/libbacktrace"
    license = "BSD-3-Clause"
    topics = ("conan", "backtrace", "stack-trace")

    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    build_requires = "autoconf/2.69", "libtool/2.4.6"

    __autotools = None
    _source_subfolder = "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.settings.compiler == "Visual Studio":
            raise ConanInvalidConfiguration("libsafec doesn't support {}/{}".format(
                self.settings.compiler, self.settings.compiler.version))
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = glob.glob("libbacktrace-*")[0]
        os.rename(extracted_dir, self._source_subfolder)

    @property
    def _autotools(self):
        if self.__autotools is None:
            self.__autotools = AutoToolsBuildEnvironment(self)
        return self.__autotools

    def _autotools_configure(self):
        if self.options.shared:
            args = ["--enable-shared", "--disable-static"]
        else:
            args = ["--disable-shared", "--enable-static"]
        self._autotools.configure(args=args)

    def build(self):
        with tools.chdir(self._source_subfolder):
            self.run("autoreconf -fiv", run_environment=True)
            self._autotools_configure()
            self._autotools.make()

    def package(self):
        with tools.chdir(self._source_subfolder):
            self._autotools.install()
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")
        tools.remove_files_by_mask(os.path.join(self.package_folder, "lib"), "*.la")

    def package_info(self):
        self.cpp_info.libs = ["backtrace"]
