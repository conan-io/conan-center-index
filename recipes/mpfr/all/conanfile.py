from conans import ConanFile, AutoToolsBuildEnvironment, CMake, tools
import os
import shutil


class MpfrConan(ConanFile):
    name = "mpfr"
    description = "The MPFR library is a C library for multiple-precision floating-point computations with " \
                  "correct rounding"
    topics = ("conan", "mpfr", "multiprecision", "math", "mathematics")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.mpfr.org/"
    license = "LGPL-3.0-or-later"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    requires = "mpir/3.0.0"
    exports_sources = "CMakeLists.txt"
    generators = "cmake"

    _source_subfolder = "source_subfolder"
    _autotools = None
    _cmake = None

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)
        if self.settings.compiler == "Visual Studio":
            shutil.copy("CMakeLists.txt",
                        os.path.join(self._source_subfolder, "CMakeLists.txt"))

    def _configure_autotools(self):
        if not self._autotools:
            args = ["--enable-thread-safe"]
            if self.options.shared:
                args.extend(["--disable-static", "--enable-shared"])
            else:
                args.extend(["--disable-shared", "--disable-static"])
            if self.settings.compiler == "clang":
                # warning: optimization flag '-ffloat-store' is not supported
                args.append("mpfr_cv_gcc_floatconv_bug=no")
            if self.settings.compiler == "clang" and self.settings.arch == "x86":
                # fatal error: error in backend: Unsupported library call operation!
                args.append("--disable-float128")
            self._autotools = AutoToolsBuildEnvironment(self)
            self._autotools.configure(args=args, configure_dir=self._source_subfolder)
        return self._autotools

    def _configure_cmake(self):
        if not self._cmake:
            self._cmake = CMake(self)
            self._cmake.configure(source_folder=self._source_subfolder)
        return self._cmake

    def build(self):
        if self.settings.compiler == "Visual Studio":
            cmake = self._configure_cmake()
            cmake.build()
        else:
            autotools = self._configure_autotools()
            autotools.make(args=["V=0"])

    def package(self):
        self.copy("COPYING", dst="licenses", src=self._source_subfolder)
        if self.settings.compiler == "Visual Studio":
            cmake = self._configure_cmake()
            cmake.install()
        else:
            autotools = self._configure_autotools()
            autotools.install()
            la = os.path.join(self.package_folder, "lib", "libmpfr.la")
            if os.path.isfile(la):
                os.unlink(la)
            tools.rmdir(os.path.join(self.package_folder, "share"))
            tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.libs = ["mpfr"]
