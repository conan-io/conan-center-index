from conans import ConanFile, tools, AutoToolsBuildEnvironment
from conan.tools.files import rename
from conan.tools.microsoft import is_msvc
from contextlib import contextmanager
import os

required_conan_version = ">=1.45.0"


class GlpkConan(ConanFile):
    name = "glpk"
    description = "GNU Linear Programming Kit"
    homepage = "https://www.gnu.org/software/glpk"
    topics = ("linear", "programming", "simplex", "solver")
    url = "https://github.com/conan-io/conan-center-index"
    license = "GPL-3.0-or-later"
    settings = "os", "arch", "compiler", "build_type"
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

    @property
    def _user_info_build(self):
        return getattr(self, "user_info_build", self.deps_user_info)

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

    def build_requirements(self):
        self.build_requires("libtool/2.4.6")
        if self._settings_build.os == "Windows" and not tools.get_env("CONAN_BASH_PATH"):
            self.build_requires("msys2/cci.latest")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version], strip_root=True,
                  destination=self._source_subfolder)

    @contextmanager
    def _build_context(self):
        if is_msvc(self):
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

    def _patch_source(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.patch(self, **patch)
        with tools.files.chdir(self, self._source_subfolder):
            self.run("{} -fiv".format(tools.get_env("AUTORECONF")), win_bash=tools.os_info.is_windows, run_environment=True)
        tools.files.replace_in_file(self, os.path.join(self._source_subfolder, "configure"),
                              r"-install_name \$rpath/",
                              "-install_name @rpath/")

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)

        self._autotools.libs = []
        yes_no = lambda v: "yes" if v else "no"
        args = [
            "--enable-shared={}".format(yes_no(self.options.shared)),
            "--enable-static={}".format(yes_no(not self.options.shared)),
            "--with-pic={}".format(yes_no(self.options.get_safe("fPIC", True)))
        ]

        if is_msvc(self):
            self._autotools.defines.append("__WOE__")
            if self.settings.compiler == "Visual Studio" and \
               tools.scm.Version(self, self.settings.compiler.version) >= "12":
                self._autotools.flags.append("-FS")
        self._autotools.configure(args=args, configure_dir=self._source_subfolder)
        return self._autotools

    def build(self):
        #self._patch_source()
        with self._build_context():
            autotools = self._configure_autotools()
            autotools.make()

    def package(self):
        self.copy("COPYING", dst="licenses", src=self._source_subfolder)
        with self._build_context():
            autotools = self._configure_autotools()
            autotools.install()
            tools.files.rm(self, os.path.join(self.package_folder, "lib"), "*.la")

        if is_msvc(self) and self.options.shared:
            pjoin = lambda p: os.path.join(self.package_folder, "lib", p)
            rename(self, pjoin("glpk.dll.lib"), pjoin("glpk.lib"))

    def package_info(self):
        self.cpp_info.set_property("cmake_find_mode", "both")
        self.cpp_info.set_property("cmake_file_name", "glpk")
        self.cpp_info.set_property("cmake_target_name", "glpk::glpk")
        self.cpp_info.set_property("pkg_config_name", "glpk")

        self.cpp_info.components["libglpk"].set_property("cmake_target_name", "glpk::glpk")
        self.cpp_info.components["libglpk"].libs = ["glpk"]

        if self.settings.os in ("FreeBSD", "Linux"):
            self.cpp_info.components["libglpk"].system_libs = ["m"]

        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment var: {}".format(bin_path))
        self.env_info.PATH.append(bin_path)

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.names["cmake_find_package"] = "glpk"
        self.cpp_info.names["cmake_find_package_multi"] = "glpk"
        self.cpp_info.components["libglpk"].names["cmake_find_package"] = "glpk"
        self.cpp_info.components["libglpk"].names["cmake_find_package_multi"] = "glpk"


