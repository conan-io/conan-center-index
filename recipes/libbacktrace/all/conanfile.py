from conans import AutoToolsBuildEnvironment, ConanFile, tools


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

    scm = {
        "type": "git",
        "url": "https://github.com/ianlancetaylor/libbacktrace.git",
        "revision": "master",
    }

    __autotools = None

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    @property
    def _autotools(self):
        if self.__autotools:
            return self.__autotools
        self.__autotools = AutoToolsBuildEnvironment(self)
        if self.options.shared:
            args = ["--enable-shared", "--disable-static"]
        else:
            args = ["--disable-shared", "--enable-static"]
        self.__autotools.configure(args=args)
        return self.__autotools

    def build(self):
        self._autotools.make()

    def package(self):
        self._autotools.install()
        self.copy("LICENSE", dst="licenses")

    def package_info(self):
        self.cpp_info.libs = ["backtrace"]
