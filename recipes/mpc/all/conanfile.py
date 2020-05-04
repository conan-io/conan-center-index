from conans import ConanFile, AutoToolsBuildEnvironment, tools
from conans.errors import ConanInvalidConfiguration
import os


class MpcConan(ConanFile):
    name = "mpc"
    description = "GNU MPC is a C library for the arithmetic of complex numbers with arbitrarily high precision " \
                  "and correct rounding of the result"
    topics = ("conan", "mpc", "multiprecision", "math", "mathematics")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://www.multiprecision.org/mpc/home.html"
    license = "LGPL-3.0-or-later"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"
    requires = "mpfr/4.0.2"

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC

    def configure(self):
        if self.settings.compiler == 'Visual Studio':
            raise ConanInvalidConfiguration("The mpc package cannot be built on Visual Studio.")
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def build(self):
        with tools.chdir(self._source_subfolder):
            args = []
            if self.options.shared:
                args.extend(["--disable-static", "--enable-shared"])
            else:
                args.extend(["--disable-shared", "--disable-static"])
            env_build = AutoToolsBuildEnvironment(self)
            env_build.configure(args=args)
            env_build.make(args=["V=0"])
            env_build.install()

    def package(self):
        self.copy(pattern="COPYING.LESSER", dst="licenses", src=self._source_subfolder)
        tools.rmdir(os.path.join(self.package_folder, "share"))
        la = os.path.join(self.package_folder, "lib", "libmpc.la")
        if os.path.isfile(la):
            os.unlink(la)

    def package_info(self):
        self.cpp_info.libs = ["mpc"]
