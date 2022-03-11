from conans import ConanFile, AutoToolsBuildEnvironment, VisualStudioBuildEnvironment, tools
from conans.errors import ConanInvalidConfiguration
from contextlib import contextmanager
import os

required_conan_version = ">=1.33.0"


class CalcephConan(ConanFile):
    name = "calceph"
    description = "C Library designed to access the binary planetary ephemeris " \
                  "files, such INPOPxx, JPL DExxx and SPICE ephemeris files."
    license = ["CECILL-C", "CECILL-B", "CECILL-2.1"]
    topics = ("conan", "calceph", "ephemeris", "astronomy", "space", "planet")
    homepage = "https://www.imcce.fr/inpop/calceph"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "threadsafe": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "threadsafe": False,
    }

    _autotools= None
    _nmake_args = None

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
        if self.settings.compiler == "Visual Studio":
            del self.options.threadsafe

    def validate(self):
        if self.settings.compiler == "Visual Studio" and self.options.shared:
            raise ConanInvalidConfiguration("calceph doesn't support shared builds with Visual Studio yet")

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def build_requirements(self):
        if self._settings_build.os == "Windows" and self.settings.compiler != "Visual Studio" and \
           not tools.get_env("CONAN_BASH_PATH"):
            self.build_requires("msys2/cci.latest")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    @contextmanager
    def _msvc_build_environment(self):
        with tools.vcvars(self):
            with tools.environment_append(VisualStudioBuildEnvironment(self).vars):
                yield

    def build(self):
        if self.settings.compiler == "Visual Studio":
            tools.replace_in_file(os.path.join(self._source_subfolder, "Makefile.vc"),
                                  "CFLAGS = /O2 /GR- /MD /nologo /EHs",
                                  "CFLAGS = /nologo /EHs")
            with tools.chdir(self._source_subfolder):
                with self._msvc_build_environment():
                    self.run("nmake -f Makefile.vc {}".format(" ".join(self._get_nmake_args())))
        else:
            autotools = self._configure_autotools()
            autotools.make()

    def _get_nmake_args(self):
        if self._nmake_args:
            return self._nmake_args
        self._nmake_args = []
        self._nmake_args.append("DESTDIR=\"{}\"".format(self.package_folder))
        self._nmake_args.extend(["ENABLEF2003=0", "ENABLEF77=0"])
        return self._nmake_args

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        args = [
            "--disable-static" if self.options.shared else "--enable-static",
            "--enable-shared" if self.options.shared else "--disable-shared",
            "--enable-thread" if self.options.threadsafe else "--disable-thread",
            "--disable-fortran",
            "--disable-python",
            "--disable-python-package-system",
            "--disable-python-package-user",
            "--disable-mex-octave",
        ]
        self._autotools.configure(args=args, configure_dir=self._source_subfolder)
        return self._autotools

    def package(self):
        self.copy(pattern="COPYING*", dst="licenses", src=self._source_subfolder)
        if self.settings.compiler == "Visual Studio":
            with tools.chdir(self._source_subfolder):
                with self._msvc_build_environment():
                    self.run("nmake -f Makefile.vc install {}".format(" ".join(self._get_nmake_args())))
            tools.rmdir(os.path.join(self.package_folder, "doc"))
        else:
            autotools = self._configure_autotools()
            autotools.install()
            tools.rmdir(os.path.join(self.package_folder, "share"))
            tools.remove_files_by_mask(os.path.join(self.package_folder, "lib"), "*.la")
        tools.rmdir(os.path.join(self.package_folder, "libexec"))

    def package_info(self):
        prefix = "lib" if self.settings.compiler == "Visual Studio" else ""
        self.cpp_info.libs = ["{}calceph".format(prefix)]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")
            if self.options.threadsafe:
                self.cpp_info.system_libs.append("pthread")

        if self.settings.compiler != "Visual Studio":
            bin_path = os.path.join(self.package_folder, "bin")
            self.output.info("Appending PATH environment variable: {}".format(bin_path))
            self.env_info.PATH.append(bin_path)
