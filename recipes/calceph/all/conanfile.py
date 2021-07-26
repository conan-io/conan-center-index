import glob
import os

from conans import ConanFile, AutoToolsBuildEnvironment, VisualStudioBuildEnvironment, tools
from conans.errors import ConanInvalidConfiguration

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
        "threadsafe": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "threadsafe": False
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
            if self.options.shared:
                raise ConanInvalidConfiguration("calceph doesn't support shared builds with Visual Studio yet")

    def build_requirements(self):
        if tools.os_info.is_windows and self.settings.compiler != "Visual Studio" and \
           "CONAN_BASH_PATH" not in os.environ:
            self.build_requires("msys2/20200517")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename(self.name + "-" + self.version, self._source_subfolder)

    def build(self):
        if self.settings.compiler == "Visual Studio":
            tools.replace_in_file(os.path.join(self._source_subfolder, "Makefile.vc"),
                                  "CFLAGS = /O2 /GR- /MD /nologo /EHs",
                                  "CFLAGS = /nologo /EHs")
            with tools.chdir(self._source_subfolder):
                with tools.vcvars(self.settings):
                    with tools.environment_append(VisualStudioBuildEnvironment(self).vars):
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
            "--disable-mex-octave"
        ]
        self._autotools.configure(args=args, configure_dir=self._source_subfolder)
        return self._autotools

    def package(self):
        self.copy(pattern="COPYING*", dst="licenses", src=self._source_subfolder)
        if self.settings.compiler == "Visual Studio":
            with tools.chdir(self._source_subfolder):
                with tools.vcvars(self.settings):
                    with tools.environment_append(VisualStudioBuildEnvironment(self).vars):
                        self.run("nmake -f Makefile.vc install {}".format(" ".join(self._get_nmake_args())))
            tools.rmdir(os.path.join(self.package_folder, "doc"))
        else:
            autotools = self._configure_autotools()
            autotools.install()
            tools.rmdir(os.path.join(self.package_folder, "share"))
            for la_file in glob.glob(os.path.join(self.package_folder, "lib", "*.la")):
                os.remove(la_file)
        tools.rmdir(os.path.join(self.package_folder, "libexec"))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os == "Linux":
            self.cpp_info.system_libs.append("m")
            if self.options.threadsafe:
                self.cpp_info.system_libs.append("pthread")

        if self.settings.compiler != "Visual Studio":
            bin_path = os.path.join(self.package_folder, "bin")
            self.output.info("Appending PATH environment variable: {}".format(bin_path))
            self.env_info.PATH.append(bin_path)
