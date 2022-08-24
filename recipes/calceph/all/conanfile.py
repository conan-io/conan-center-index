from conans import ConanFile, AutoToolsBuildEnvironment, VisualStudioBuildEnvironment, tools
from conan.errors import ConanInvalidConfiguration
from contextlib import contextmanager
import functools
import os

required_conan_version = ">=1.33.0"


class CalcephConan(ConanFile):
    name = "calceph"
    description = "C Library designed to access the binary planetary ephemeris " \
                  "files, such INPOPxx, JPL DExxx and SPICE ephemeris files."
    license = ["CECILL-C", "CECILL-B", "CECILL-2.1"]
    topics = ("calceph", "ephemeris", "astronomy", "space", "planet")
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

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _is_msvc(self):
        return str(self.settings.compiler) in ["Visual Studio", "msvc"]

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if self._is_msvc:
            del self.options.threadsafe

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.cppstd
        del self.settings.compiler.libcxx

    def validate(self):
        if self._is_msvc and self.options.shared:
            raise ConanInvalidConfiguration("calceph doesn't support shared builds with Visual Studio yet")

    def build_requirements(self):
        if self._settings_build.os == "Windows" and not self._is_msvc and \
           not tools.get_env("CONAN_BASH_PATH"):
            self.build_requires("msys2/cci.latest")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def build(self):
        if self._is_msvc:
            tools.files.replace_in_file(self, os.path.join(self._source_subfolder, "Makefile.vc"),
                                  "CFLAGS = /O2 /GR- /MD /nologo /EHs",
                                  "CFLAGS = /nologo /EHs")
            with tools.files.chdir(self, self._source_subfolder):
                with self._msvc_build_environment():
                    self.run("nmake -f Makefile.vc {}".format(self._nmake_args))
        else:
            # relocatable shared lib on macOS
            tools.files.replace_in_file(self, os.path.join(self._source_subfolder, "configure"),
                                  "-install_name \\$rpath/",
                                  "-install_name @rpath/")
            autotools = self._configure_autotools()
            autotools.make()

    @contextmanager
    def _msvc_build_environment(self):
        with tools.vcvars(self):
            with tools.environment_append(VisualStudioBuildEnvironment(self).vars):
                yield

    @property
    def _nmake_args(self):
        return " ".join([
            "DESTDIR=\"{}\"".format(self.package_folder),
            "ENABLEF2003=0",
            "ENABLEF77=0",
        ])

    @functools.lru_cache(1)
    def _configure_autotools(self):
        autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        autotools.libs = []
        yes_no = lambda v: "yes" if v else "no"
        args = [
            "--enable-static={}".format(yes_no(not self.options.shared)),
            "--enable-shared={}".format(yes_no(self.options.shared)),
            "--enable-thread={}".format(yes_no(self.options.threadsafe)),
            "--disable-fortran",
            "--disable-python",
            "--disable-python-package-system",
            "--disable-python-package-user",
            "--disable-mex-octave",
        ]
        autotools.configure(args=args, configure_dir=self._source_subfolder)
        return autotools

    def package(self):
        self.copy(pattern="COPYING*", dst="licenses", src=self._source_subfolder)
        if self._is_msvc:
            with tools.files.chdir(self, self._source_subfolder):
                with self._msvc_build_environment():
                    self.run("nmake -f Makefile.vc install {}".format(self._nmake_args))
            tools.files.rmdir(self, os.path.join(self.package_folder, "doc"))
        else:
            autotools = self._configure_autotools()
            autotools.install()
            tools.files.rmdir(self, os.path.join(self.package_folder, "share"))
            tools.files.rm(self, os.path.join(self.package_folder, "lib"), "*.la")
        tools.files.rmdir(self, os.path.join(self.package_folder, "libexec"))

    def package_info(self):
        prefix = "lib" if self._is_msvc else ""
        self.cpp_info.libs = ["{}calceph".format(prefix)]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")
            if self.options.threadsafe:
                self.cpp_info.system_libs.append("pthread")

        if not self._is_msvc:
            bin_path = os.path.join(self.package_folder, "bin")
            self.output.info("Appending PATH environment variable: {}".format(bin_path))
            self.env_info.PATH.append(bin_path)
