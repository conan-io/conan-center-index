from conan import ConanFile
from conan.tools import files
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version
from conans import AutoToolsBuildEnvironment
from conans.tools import environment_append, get_env, os_info, vcvars, unix_path
from contextlib import contextmanager
import os

required_conan_version = ">=1.47.0"


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
        if self._settings_build.os == "Windows" and not get_env("CONAN_BASH_PATH"):
            self.build_requires("msys2/cci.latest")
        if self.settings.compiler == "Visual Studio":
            self.build_requires("automake/1.16.5")

    def source(self):
        files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    @contextmanager
    def _build_context(self):
        if is_msvc(self):
            with vcvars(self):
                env = {
                    "CC": "cl -nologo",
                    "CXX": "cl -nologo",
                    "LD": "link -nologo",
                    "AR": "{} lib".format(unix_path(self.deps_user_info["automake"].ar_lib)),
                }
                with environment_append(env):
                    yield
        else:
            yield

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(
            self, win_bash=os_info.is_windows)

        def yes_no(v): return "yes" if v else "no"
        args = [
            "--enable-shared={}".format(yes_no(self.options.shared)),
            "--enable-static={}".format(yes_no(not self.options.shared)),
        ]
        if is_msvc(self):
            self._autotools.cxx_flags.append("-EHsc")
            if Version(self.settings.compiler.version) >= "12":
                self._autotools.flags.append("-FS")
        self._autotools.configure(
            args=args, configure_dir=self._source_subfolder)
        return self._autotools

    def build(self):
        with self._build_context():
            self._configure_autotools()
            self._autotools.make()

    def package(self):
        self._autotools.install()
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        files.rm(self, os.path.join(self.package_folder, "lib"), "*.la")
        files.rmdir(self, os.path.join(
            self.package_folder, "lib", "pkgconfig"))
        if self.settings.compiler == "Visual Studio" and self.options.shared:
            for lib in ("opencore-amrwb", "opencore-amrnb"):
                files.rename(self, os.path.join(self.package_folder, "lib", "{}.dll.lib".format(lib)),
                             os.path.join(self.package_folder, "lib", "{}.lib".format(lib)))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "opencore-amr")
        self.cpp_info.set_property(
            "cmake_target_name", "opencore-amr::opencore-amr")
        for lib in ("opencore-amrwb", "opencore-amrnb"):
            self.cpp_info.components[lib].set_property(
                "cmake_target_name", f'opencore-amr::{lib}')
            self.cpp_info.components[lib].set_property("pkg_config_name", lib)
            self.cpp_info.components[lib].libs = [lib]
            # TODO: to remove in conan v2 once cmake_find_package* & pkg_config generator removed
            self.cpp_info.components[lib].names["pkg_config"] = lib
