from conan.tools.files import rename
from conans import AutoToolsBuildEnvironment, ConanFile, tools
from conan.errors import ConanInvalidConfiguration
import contextlib
import functools
import os

required_conan_version = ">=1.33.0"


class LibbacktraceConan(ConanFile):
    name = "libbacktrace"
    description = "A C library that may be linked into a C/C++ program to produce symbolic backtraces."
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/ianlancetaylor/libbacktrace"
    license = "BSD-3-Clause"
    topics = ("backtrace", "stack-trace")
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
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

    def export_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def validate(self):
        if self._is_msvc and self.options.shared:
            raise ConanInvalidConfiguration("libbacktrace shared is not supported with Visual Studio")

    def build_requirements(self):
        if self._settings_build.os == "Windows" and not tools.get_env("CONAN_BASH_PATH"):
            self.build_requires("msys2/cci.latest")
        if self._is_msvc:
            self.build_requires("automake/1.16.4")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    @property
    def _user_info_build(self):
        return getattr(self, "user_info_build", self.deps_user_info)

    @contextlib.contextmanager
    def _build_context(self):
        if self._is_msvc:
            with tools.vcvars(self):
                env = {
                    "CC": "{} cl -nologo".format(tools.microsoft.unix_path(self, self._user_info_build["automake"].compile)),
                    "CXX": "{} cl -nologo".format(tools.microsoft.unix_path(self, self._user_info_build["automake"].compile)),
                    "LD": "{} link -nologo".format(tools.microsoft.unix_path(self, self._user_info_build["automake"].compile)),
                    "AR": "{} lib".format(tools.microsoft.unix_path(self, self._user_info_build["automake"].ar_lib)),
                }
                with tools.environment_append(env):
                    yield
        else:
            yield

    @functools.lru_cache(1)
    def _configure_autotools(self):
        autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        autotools.libs = []
        if (self.settings.compiler == "Visual Studio" and tools.Version(self.settings.compiler.version) >= "12") or \
           str(self.settings.compiler) == "msvc":
            autotools.flags.append("-FS")
        yes_no = lambda v: "yes" if v else "no"
        args = [
            "--enable-shared={}".format(yes_no(self.options.shared)),
            "--enable-static={}".format(yes_no(not self.options.shared)),
        ]
        autotools.configure(args=args, configure_dir=self._source_subfolder)
        return autotools

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.patch(self, **patch)
        # relocatable shared lib on macOS
        tools.files.replace_in_file(self, os.path.join(self._source_subfolder, "configure"),
                              "-install_name \\$rpath/",
                              "-install_name @rpath/")

    def build(self):
        self._patch_sources()
        with self._build_context():
            autotools = self._configure_autotools()
            autotools.make()

    def package(self):
        with self._build_context():
            autotools = self._configure_autotools()
            autotools.install()
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")
        lib_folder = os.path.join(self.package_folder, "lib")
        if self._is_msvc:
            rename(self, os.path.join(lib_folder, "libbacktrace.lib"),
                         os.path.join(lib_folder, "backtrace.lib"))
        tools.files.rm(self, lib_folder, "*.la")

    def package_info(self):
        self.cpp_info.libs = ["backtrace"]
