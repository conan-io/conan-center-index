from conans import ConanFile, AutoToolsBuildEnvironment, tools
from contextlib import contextmanager
import os

required_conan_version = ">=1.33.0"


class OpencoreAmrConan(ConanFile):
    name = "opencore-amr"
    homepage = "https://sourceforge.net/projects/opencore-amr/"
    description = "OpenCORE Adaptive Multi Rate (AMR) speech codec library implementation."
    topics = ("audio-codec", "amr", "opencore")
    url = "https://github.com/conan-io/conan-center-index"
    license = "Apache-2.0"
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False, 
        "fPIC": True,
    }

    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def build_requirements(self):
        if self._settings_build.os == "Windows" and not tools.get_env("CONAN_BASH_PATH"):
            self.build_requires("msys2/cci.latest")
        if self.settings.compiler == "Visual Studio":
            self.build_requires("automake/1.16.4")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    @contextmanager
    def _build_context(self):
        if self.settings.compiler == "Visual Studio":
            with tools.vcvars(self):
                env = {
                    "CC": "cl -nologo",
                    "CXX": "cl -nologo",
                    "LD": "link -nologo",
                    "AR": "{} lib".format(tools.unix_path(self.deps_user_info["automake"].ar_lib)),
                }
                with tools.environment_append(env):
                    yield
        else:
            yield

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        yes_no = lambda v: "yes" if v else "no"
        args = [
            "--enable-shared={}".format(yes_no(self.options.shared)),
            "--enable-static={}".format(yes_no(not self.options.shared)),
        ]
        if self.settings.compiler == "Visual Studio":
            self._autotools.cxx_flags.append("-EHsc")
            if tools.Version(self.settings.compiler.version) >= "12":
                self._autotools.flags.append("-FS")
        self._autotools.configure(args=args, configure_dir=self._source_subfolder)
        return self._autotools

    def build(self):
        with self._build_context():
            self._configure_autotools()
            self._autotools.make()

    def package(self):
        self._autotools.install()
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        tools.files.rm(self, os.path.join(self.package_folder, "lib"), "*.la")
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        if self.settings.compiler == "Visual Studio" and self.options.shared:
            for lib in ("opencore-amrwb", "opencore-amrnb"):
                tools.files.rename(self, os.path.join(self.package_folder, "lib", "{}.dll.lib".format(lib)),
                             os.path.join(self.package_folder, "lib", "{}.lib".format(lib)))

    def package_info(self):
        for lib in ("opencore-amrwb", "opencore-amrnb"):
            self.cpp_info.components[lib].names["pkg_config"] = lib
            self.cpp_info.components[lib].libs = [lib]
