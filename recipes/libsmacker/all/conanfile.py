from conans import AutoToolsBuildEnvironment, ConanFile, tools
import contextlib
import os

required_conan_version = ">=1.33.0"


class LibsmackerConan(ConanFile):
    name = "libsmacker"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://libsmacker.sourceforge.net"
    topics = ("libsmacker", "decoding ", "smk", "smacker", "video", "file")
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

    exports_sources = "patches/*"
    _autotools = None

    @property
    def _source_subfolder(self):
        return os.path.join(self.source_folder, "source_subfolder")

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

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
        if self._settings_build.os == "Windows" and not tools.get_env("CONAN_BASH_PATH"):
            self.build_requires("msys2/cci.latest")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    @contextlib.contextmanager
    def _build_context(self):
        if self.settings.compiler == "Visual Studio":
            with tools.vcvars(self):
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
        if self.settings.compiler == "Visual Studio" and tools.scm.Version(self, self.settings.compiler.version) >= "12":
            self._autotools.flags.append("-FS")
        yes_no = lambda v: "yes" if v else "no"
        args = [
            "--enable-shared={}".format(yes_no(self.options.shared)),
            "--enable-static={}".format(yes_no(not self.options.shared)),
        ]
        self._autotools.configure(configure_dir=self._source_subfolder, args=args)
        return self._autotools

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.patch(self, **patch)
        with tools.files.chdir(self, self._source_subfolder):
            self.run("{} -fiv".format(tools.get_env("AUTORECONF")), win_bash=tools.os_info.is_windows)
        with self._build_context():
            autotools = self._configure_autotools()
            autotools.make()

    def package(self):
        self.copy("COPYING", src=self._source_subfolder, dst="licenses")
        with self._build_context():
            autotools = self._configure_autotools()
            autotools.install()

        tools.files.rm(self, os.path.join(self.package_folder, "lib"), "*.la")
        if self.settings.compiler == "Visual Studio" and self.options.shared:
            os.rename(os.path.join(self.package_folder, "lib", "smacker.dll.lib"),
                      os.path.join(self.package_folder, "lib", "smacker.lib"))

    def package_info(self):
        self.cpp_info.libs = ["smacker"]
