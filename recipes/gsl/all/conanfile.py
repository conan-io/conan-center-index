from conans import ConanFile, tools, AutoToolsBuildEnvironment
from contextlib import contextmanager
import os

required_conan_version = ">=1.33.0"

class GslConan(ConanFile):
    name = "gsl"
    description = "GNU Scientific Library"
    homepage = "https://www.gnu.org/software/gsl"
    topics = ("numerical", "math", "random", "scientific")
    url = "https://github.com/conan-io/conan-center-index"
    license = "GPL-3.0-or-later"

    settings = "os", "compiler", "build_type", "arch"

    options = {
        "shared": [True, False],
        "fPIC": [True, False]
    }

    default_options = {
        "shared": False,
        "fPIC": True
    }

    exports_sources = "patches/*"

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
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], strip_root=True,
                  destination=self._source_subfolder)

    def build_requirements(self):
        self.build_requires("libtool/2.4.6")
        if self._settings_build.os == "Windows" and not tools.get_env("CONAN_BASH_PATH"):
            self.build_requires("msys2/cci.latest")

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

    def _patch_source(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        with tools.chdir(self._source_subfolder):
            self.run("{} -fiv".format(tools.get_env("AUTORECONF")), win_bash=tools.os_info.is_windows, run_environment=True)
        tools.replace_in_file(os.path.join(self._source_subfolder, "configure"),
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
        ]
        if self.settings.os == "Windows":
            self._autotools.defines.extend(["HAVE_WIN_IEEE_INTERFACE", "WIN32"])
            if self.options.shared:
                self._autotools.defines.append("GSL_DLL")

        if self.settings.os == "Linux" and "x86" in self.settings.arch:
            self._autotools.defines.append("HAVE_GNUX86_IEEE_INTERFACE")

        if self.settings.compiler == "Visual Studio":
            self._autotools.flags.append("-FS")
            self._autotools.cxx_flags.append("-EHsc")
            args.extend([
                "ac_cv_func_memcpy=yes",
                "ac_cv_func_memmove=yes",
                "ac_cv_c_c99inline=no",
            ])
        self._autotools.configure(args=args, configure_dir=self._source_subfolder)
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

        os.unlink(os.path.join(self.package_folder, "bin", "gsl-config"))

        if self.settings.compiler == "Visual Studio" and self.options.shared:
            pjoin = lambda p: os.path.join(self.package_folder, "lib", p)
            tools.rename(pjoin("gsl.dll.lib"), pjoin("gsl.lib"))
            tools.rename(pjoin("gslcblas.dll.lib"), pjoin("gslcblas.lib"))

    def package_info(self):
        self.cpp_info.names["pkg_config"] = "gsl"

        self.cpp_info.filenames["cmake_find_package"] = "GSL"
        self.cpp_info.filenames["cmake_find_package_multi"] = "GSL"

        self.cpp_info.names["cmake_find_package"] = "GSL"
        self.cpp_info.names["cmake_find_package_multi"] = "GSL"

        self.cpp_info.components["libgsl"].names["cmake_find_package"] = "gsl"
        self.cpp_info.components["libgsl"].names["cmake_find_package_multi"] = "gsl"
        self.cpp_info.components["libgsl"].libs = ["gsl"]
        self.cpp_info.components["libgsl"].requires = ["libgslcblas"]

        self.cpp_info.components["libgslcblas"].names["cmake_find_package"] = "gslcblas"
        self.cpp_info.components["libgslcblas"].names["cmake_find_package_multi"] = "gslcblas"
        self.cpp_info.components["libgslcblas"].libs = ["gslcblas"]

        if self.settings.os in ("FreeBSD", "Linux"):
            self.cpp_info.components["libgsl"].system_libs = ["m"]
            self.cpp_info.components["libgslcblas"].system_libs = ["m"]

        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment var: {}".format(bin_path))
        self.env_info.PATH.append(bin_path)
