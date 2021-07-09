from conans import ConanFile, tools, AutoToolsBuildEnvironment
from contextlib import contextmanager
import os


class GslConan(ConanFile):
    name = "gsl"
    license = "GPL-3.0-or-later"
    topics = ("numerical", "math", "random", "scientific")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.gnu.org/software/gsl"
    description = "GNU Scientific Library"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], strip_root=True,
                  destination=self._source_subfolder)

    def build_requirements(self):
        self.build_requires("libtool/2.4.6")
        if tools.os_info.is_windows and not tools.get_env("CONAN_BASH_PATH"):
            self.build_requires("msys2/cci.latest")

    @contextmanager
    def _build_context(self):
        if self.settings.compiler == "Visual Studio":
            with tools.vcvars(self.settings):
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

    def _patch_source(self):
        tools.replace_in_file(os.path.join(self._source_subfolder, "configure"),
                              r"-install_name \$rpath/",
                              "-install_name @rpath/")

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        if self.settings.compiler == "Visual Studio":
            self._autotools.flags.append("-FS")
            self._autotools.cxx_flags.append("-EHsc")
        args = [
            "--enable-shared" if self.options.shared else "--disable-shared",
            "--enable-static" if not self.options.shared else "--disable-static",
        ]
        self._autotools.configure(args=args,configure_dir=self._source_subfolder)
        return self._autotools

    def build(self):
        self._patch_source()
        with self._build_context():
            autotools = self._configure_autotools()
            autotools.make()

    def package(self):
        self.copy("COPYING", dst="licenses", src=self._source_subfolder)
        with self._build_context():
            autotools = self._configure_autotools()
            autotools.install()
        tools.rmdir(os.path.join(self.package_folder, "share"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.remove_files_by_mask(os.path.join(self.package_folder, "lib"), "*.la")
        tools.remove_files_by_mask(os.path.join(self.package_folder, "include", "gsl"), "*.c")

    def package_info(self):
        self.cpp_info.names["pkg_config"] = "gsl"
        self.cpp_info.names["cmake_find_package"] = "GSL"
        self.cpp_info.names["cmake_find_package_multi"] = "GSL"
        self.cpp_info.components["libgsl"].names["cmake_find_package"] = "gsl"
        self.cpp_info.components["libgsl"].names["cmake_find_package_multi"] = "gsl"
        self.cpp_info.components["libgsl"].libs = ["gsl"]
        self.cpp_info.components["libgslcblas"].names["cmake_find_package"] = "gslcblas"
        self.cpp_info.components["libgslcblas"].names["cmake_find_package_multi"] = "gslcblas"
        self.cpp_info.components["libgslcblas"].libs = ["gslcblas"]
        if self.settings.os == "Linux":
            self.cpp_info.components["libgsl"].system_libs = ["m"]
            self.cpp_info.components["libgslcblas"].system_libs = ["m"]
        bin_path = os.path.join(self.package_folder, "bin")
        self.env_info.PATH.append(bin_path)
