from conans import AutoToolsBuildEnvironment, ConanFile, tools
from contextlib import contextmanager
import os

required_conan_version = ">=1.29.1"


class LibsmackerConan(ConanFile):
    name = "libsmacker"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://libsmacker.sourceforge.net"
    topics = ("conan", "libsmacker", "decoding ", "smk", "smacker", "video", "file")
    license = "LGPL-2.1-or-later"
    description = "A C library for decoding .smk Smacker Video files"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }
    settings = "os", "arch", "compiler", "build_type"
    exports_sources = "patches/**"
    _autotools = None

    @property
    def _source_subfolder(self):
        return os.path.join(self.source_folder, "source_subfolder")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.cppstd
        del self.settings.compiler.libcxx

    def build_requirements(self):
        self.build_requires("libtool/2.4.6")
        if tools.os_info.is_windows:
            self.build_requires("msys2/20200517")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        v = tools.Version(self.version)
        os.rename("libsmacker-{}.{}.{}".format(v.major, v.minor, v.patch), self._source_subfolder)

    @contextmanager
    def _build_context(self):
        if self.settings.compiler == "Visual Studio":
            with tools.vcvars(self.settings):
                env = {
                    "CC": "cl -nologo",
                    "CXX": "cl -nologo",
                    "LD": "link -nologo",
                }
                with tools.environment_append(env):
                    yield
        else:
            yield

    def _configure_autotools(self):
        if self._autotools is not None:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self,win_bash=tools.os_info.is_windows)
        self._autotools.libs = []
        yes_no = lambda v: "yes" if v else "no"
        if self.settings.compiler == "Visual Studio":
            self._autotools.flags.append("-FS")
        args = [
            "--enable-shared={}".format(yes_no(self.options.shared)),
            "--enable-static={}".format(yes_no(not self.options.shared)),
        ]
        self._autotools.configure(configure_dir=self._source_subfolder, args=args)
        return self._autotools

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        with tools.chdir(self._source_subfolder):
            self.run("{} -fiv".format(tools.get_env("AUTORECONF")), win_bash=tools.os_info.is_windows)
        with self._build_context():
            autotools = self._configure_autotools()
            autotools.make()

    def package(self):
        self.copy("COPYING", src=self._source_subfolder, dst="licenses")
        with self._build_context():
            autotools = self._configure_autotools()
            autotools.install()

        tools.remove_files_by_mask(os.path.join(self.package_folder, "lib"), "*.la")
        if self.settings.compiler == "Visual Studio" and self.options.shared:
            os.rename(os.path.join(self.package_folder, "lib", "smacker.dll.lib"),
                      os.path.join(self.package_folder, "lib", "smacker.lib"))

    def package_info(self):
        self.cpp_info.libs = ["smacker"]
