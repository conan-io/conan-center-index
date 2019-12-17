from conans import ConanFile, AutoToolsBuildEnvironment, tools
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
    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"
    requires = "gmp/6.1.2"

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

    def build(self):
        with tools.chdir(self._source_subfolder):
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
            env_build = AutoToolsBuildEnvironment(self)
            env_build.configure(args=args)
            env_build.make(args=["V=0"])
            env_build.install()

    def package(self):
        self.copy("COPYING", dst="licenses", src=self._source_subfolder)
        la = os.path.join(self.package_folder, "lib", "libmpfr.la")
        if os.path.isfile(la):
            os.unlink(la)
        shutil.rmtree(os.path.join(self.package_folder, "share"), ignore_errors=True)
        shutil.rmtree(os.path.join(self.package_folder, "lib", "pkgconfig"), ignore_errors=True)

    def package_info(self):
        self.cpp_info.libs = ["mpfr"]
