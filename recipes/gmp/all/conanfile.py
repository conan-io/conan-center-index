from conans import ConanFile, AutoToolsBuildEnvironment, tools
from conans.errors import ConanInvalidConfiguration
import contextlib
import functools
import os
import stat

required_conan_version = ">=1.33.0"


class GmpConan(ConanFile):
    name = "gmp"
    description = "GMP is a free library for arbitrary precision arithmetic, operating on signed integers, rational numbers, and floating-point numbers."
    url = "https://github.com/conan-io/conan-center-index"
    topics = ("gmp", "math", "arbitrary", "precision", "integer")
    license = ("LGPL-3.0", "GPL-2.0")
    homepage = "https://gmplib.org"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "disable_assembly": [True, False],
        "enable_fat": [True, False],
        "run_checks": [True, False],
        "enable_cxx": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "disable_assembly": True,
        "enable_fat": False,
        "run_checks": False,
        "enable_cxx": True,
    }

    exports_sources = "patches/*"


    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if self.settings.arch not in ["x86", "x86_64"]:
            del self.options.enable_fat

    def configure(self):
        if self.settings.compiler == "Visual Studio" and self.options.shared:
            raise ConanInvalidConfiguration("Cannot build a shared library using Visual Studio: some error occurs at link time")
        if self.options.shared:
            del self.options.fPIC
        if self.options.get_safe("enable_fat"):
            del self.options.disable_assembly
        if not self.options.enable_cxx:
            del self.settings.compiler.libcxx
            del self.settings.compiler.cppstd

    def package_id(self):
        del self.info.options.run_checks  # run_checks doesn't affect package's ID

    def build_requirements(self):
        self.build_requires("m4/1.4.19")
        if self._settings_build.os == "Windows" and not tools.get_env("CONAN_BASH_PATH"):
            self.build_requires("msys2/cci.latest")
        if self.settings.compiler == "Visual Studio":
            self.build_requires("yasm/1.3.0")
            self.build_requires("automake/1.16.4")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], destination=self._source_subfolder, strip_root=True)

    @functools.lru_cache(1)
    def _configure_autotools(self):
        autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        if tools.is_apple_os(self.settings.os):
            configure_file = os.path.join(self._source_subfolder, "configure")
            tools.replace_in_file(configure_file, r"-install_name \$rpath/", "-install_name ")
            configure_stats = os.stat(configure_file)
            os.chmod(configure_file, configure_stats.st_mode | stat.S_IEXEC)
        yes_no = lambda v: "yes" if v else "no"
        configure_args = [
            "--with-pic={}".format(yes_no(self.options.get_safe("fPIC", True))),
            "--enable-assembly={}".format(yes_no(not self.options.get_safe("disable_assembly", False))),
            "--enable-fat={}".format(yes_no(self.options.get_safe("enable_fat", False))),
            "--enable-cxx={}".format(yes_no(self.options.enable_cxx)),
            "--enable-shared={}".format(yes_no(self.options.shared)),
            "--enable-static={}".format(yes_no(not self.options.shared)),
            "--srcdir={}".format(os.path.join(self.source_folder, self._source_subfolder).replace("\\", "/")),
        ]
        if self.settings.compiler == "Visual Studio":
            configure_args.extend([
                "ac_cv_c_restrict=restrict",
                "gmp_cv_asm_label_suffix=:",
                "lt_cv_sys_global_symbol_pipe=cat",  # added to get further in shared MSVC build, but it gets stuck later
            ])
            if tools.Version(self.settings.compiler.version) >= 12:
                autotools.flags.append("-FS")
            autotools.cxx_flags.append("-EHsc")
        autotools.configure(args=configure_args, configure_dir=self._source_subfolder)
        return autotools

    @contextlib.contextmanager
    def _build_context(self):
        if self.settings.compiler == "Visual Studio":
            with tools.vcvars(self):
                yasm_machine = {
                    "x86": "x86",
                    "x86_64": "amd64",
                }[str(self.settings.arch)]
                env = {
                    "CC": "cl -nologo",
                    "CCAS": "{} -a x86 -m {} -p gas -r raw -f win32 -g null -X gnu".format(os.path.join(self.build_folder, "yasm_wrapper.sh").replace("\\", "/"), yasm_machine),
                    "CXX": "cl -nologo",
                    "AR": "{} lib".format(self.deps_user_info["automake"].ar_lib.replace("\\", "/")),
                    "LD": "link -nologo",
                    "NM": "python {}".format(tools.unix_path(os.path.join(self.build_folder, "dumpbin_nm.py"))),
                }
                with tools.environment_append(env):
                    yield
        else:
            yield

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        with self._build_context():
            autotools = self._configure_autotools()
            autotools.make()
            # INFO: According to the gmp readme file, make check should not be omitted, but it causes timeouts on the CI server.
            if self.options.run_checks:
                autotools.make(args=["check"])

    def package(self):
        self.copy("COPYINGv2", dst="licenses", src=self._source_subfolder)
        self.copy("COPYING.LESSERv3", dst="licenses", src=self._source_subfolder)
        with self._build_context():
            autotools = self._configure_autotools()
            autotools.install()

        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "share"))
        tools.remove_files_by_mask(os.path.join(self.package_folder, "lib"), "*.la")

    def package_info(self):
        self.cpp_info.components["libgmp"].libs = ["gmp"]
        self.cpp_info.components["libgmp"].names["cmake_find_package"] = "GMP"
        self.cpp_info.components["libgmp"].names["cmake_find_package_multi"] = "GMP"
        self.cpp_info.components["libgmp"].names["pkg_config"] = "gmp"
        if self.options.enable_cxx:
            self.cpp_info.components["gmpxx"].libs = ["gmpxx"]
            self.cpp_info.components["gmpxx"].requires = ["libgmp"]
            self.cpp_info.components["gmpxx"].names["cmake_find_package"] = "GMPXX"
            self.cpp_info.components["gmpxx"].names["cmake_find_package_multi"] = "GMPXX"
            self.cpp_info.components["gmpxx"].names["pkg_config"] = "gmpxx"
