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
    options = {"shared": [True, False], "fPIC": [True, False], "exact_int": ["gmp", "mpir"]}
    default_options = {"shared": False, "fPIC": True, "exact_int": "gmp"}
    exports_sources = "patches/**"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    _autotools = None

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def requirements(self):
        self.requires("mpfr/4.1.0")
        # FIXME: DO AUTOTOOLS NEED GMP/MPIR???????
        if self.options.exact_int == "gmp":
            self.requires("gmp/6.2.1")
        elif self.options.exact_int == "mpir":
            self.requires("mpir/3.0.0")

    def build_requirements(self):
        if tools.os_info.is_windows and not tools.get_env("CONAN_BASH_PATH") and self.settings.compiler != "Visual Studio":
            self.build_requires("msys2/20200517")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        if self.options.shared:
            self._autotools.defines.append("MPC_SHARED")
        yes_no = lambda v: "yes" if v else "no"
        args = [
            "--enable-shared={}".format(yes_no(self.options.shared)),
            "--enable-static={}".format(yes_no(not self.options.shared)),
        ]
        self._autotools.configure(args=args, configure_dir=self._source_subfolder)
        return self._autotools

    def _nmake_run(self):
        autotools = AutoToolsBuildEnvironment(self)
        autotools.libs = []
        autotools.flags.append("-EHs")
        if self.options.shared:
            autotools.defines.append("MPC_SHARED")
        with tools.chdir(self._source_subfolder):
            with tools.vcvars(self.settings):
                self.run("nmake /f Makefile.vc STATIC={} GMPDIR=\"{}\" MPFR=\"{}\" CDEFAULTFLAGS=\"{}\" DESTDIR=\"{}\" GMPMUSTBEDLL=\"\"".format(
                    "0" if self.options.shared else "1",
                    self.deps_cpp_info[str(self.options.exact_int)].rootpath,
                    self.deps_cpp_info["mpfr"].rootpath,
                    "{} {}".format(autotools.vars["CPPFLAGS"], autotools.vars["CFLAGS"]),
                    self.package_folder,
                ), run_environment=True)

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        if self.options.exact_int == "mpir":
            tools.replace_in_file(os.path.join(self._source_subfolder, "Makefile.vc"),
                                  "libmpfr.lib", "mpfr.lib")
            tools.replace_in_file(os.path.join(self._source_subfolder, "Makefile.vc"),
                                  "gmp.lib", "mpir.lib")
        if self.settings.compiler == "Visual Studio":
            self._nmake_run()
        else:
            autotools = self._configure_autotools()
            autotools.make()

    def package(self):
        self.copy(pattern="COPYING.LESSER", dst="licenses", src=self._source_subfolder)
        if self.settings.compiler == "Visual Studio":
            self.copy("libmpc.lib", src=self._source_subfolder, dst="lib", keep_path=False)
            os.rename(os.path.join(self.package_folder, "lib", "libmpc.lib"),
                      os.path.join(self.package_folder, "lib", "mpc.lib"))
            self.copy("libmpc.dll", src=self._source_subfolder, dst="bin", keep_path=False)
            self.copy("mpc.h", src=os.path.join(self._source_subfolder, "src"), dst="include")
        else:
            autotools = self._configure_autotools()
            autotools.install()
            tools.rmdir(os.path.join(self.package_folder, "share"))
            os.unlink(os.path.join(self.package_folder, "lib", "libmpc.la"))

    def package_info(self):
        self.cpp_info.libs = ["mpc"]
