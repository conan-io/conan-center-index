from conans import AutoToolsBuildEnvironment, ConanFile, tools
import os


class Argtable2Conan(ConanFile):
    name = "argtable2"
    description = "Argtable is an ANSI C library for parsing GNU style command line options with a minimum of fuss."
    topics = ("conan", "argtable2", "argument", "parsing", "getopt")
    license = "LGPL-2.0+"
    homepage = "http://argtable.sourceforge.net/"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }
    generators = "cmake", "pkg_config", "cmake_find_package"
    exports_sources = "patches/**"

    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def build_requirements(self):
        if tools.os_info.is_windows and self.settings.compiler != "Visual Studio":
            self.build_requires("msys2/20200517")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("argtable{}".format(self.version.replace(".", "-")), self._source_subfolder)

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        yes_no = lambda v: "yes" if v else "no"
        conf_args = [
            "--enable-shared={}".format(yes_no(self.options.shared)),
            "--enable-static={}".format(yes_no(not self.options.shared)),
        ]
        self._autotools.configure(args=conf_args, configure_dir=self._source_subfolder)
        return self._autotools

    def _run_nmake(self, target):
        autotools = AutoToolsBuildEnvironment(self)
        autotools.libs = []
        vars = " ".join("CONAN_{}=\"{}\"".format(k, v) for k, v in autotools.vars.items())
        with tools.vcvars(self.settings):
            with tools.chdir(os.path.join(self._source_subfolder, "src")):
                self.run("nmake -f Makefile.nmake {} {}".format(target, vars), run_environment=True)

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        if self.settings.compiler == "Visual Studio":
            self._run_nmake("argtable2.dll" if self.options.shared else "argtable2.lib")
        else:
            autotools = self._configure_autotools()
            autotools.make()

    def package(self):
        self.copy("COPYING", src=self._source_subfolder, dst="licenses")
        if self.settings.compiler == "Visual Studio":
            self.copy("*.lib", src=os.path.join(self._source_subfolder, "src"), dst="lib")
            self.copy("*.dll", src=os.path.join(self._source_subfolder, "src"), dst="bin")
            self.copy("argtable2.h", src=os.path.join(self._source_subfolder, "src"), dst="include")
            if self.options.shared:
                os.rename(os.path.join(self.package_folder, "lib", "impargtable2.lib"),
                          os.path.join(self.package_folder, "lib", "argtable2.lib"))
        else:
            autotools = self._configure_autotools()
            autotools.install()

            tools.remove_files_by_mask(os.path.join(self.package_folder, "lib"), "*.la")
            tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
            tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.libs = ["argtable2"]
        self.cpp_info.names["pkg_config"] = "argtable2"
