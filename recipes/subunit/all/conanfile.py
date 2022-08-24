from conans import AutoToolsBuildEnvironment, ConanFile, tools
from conan.errors import ConanInvalidConfiguration
import contextlib
import glob
import os

required_conan_version = ">=1.33.0"


class SubunitConan(ConanFile):
    name = "subunit"
    description = "A streaming protocol for test results"
    topics = "subunit", "streaming", "protocol", "test", "results"
    license = "Apache-2.0", "BSD-3-Clause"
    homepage = "https://launchpad.net/subunit"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
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

    def requirements(self):
        self.requires("cppunit/1.15.1")

    def build_requirements(self):
        if self._settings_build.os == "Windows" and not tools.get_env("CONAN_BASH_PATH"):
            self.build_requires("msys2/cci.latest")
        if self.settings.compiler == "Visual Studio":
            self.build_requires("automake/1.16.3")

    def validate(self):
        if self.settings.os == "Windows" and self.options.shared:
            raise ConanInvalidConfiguration("Cannot build shared subunit libraries on Windows")
        if self.settings.compiler == "apple-clang" and tools.scm.Version(self, self.settings.compiler.version) < "10":
            # Complete error is:
            # make[2]: *** No rule to make target `/Applications/Xcode-9.4.app/Contents/Developer/Platforms/MacOSX.platform/Developer/SDKs/MacOSX10.13.sdk/System/Library/Perl/5.18/darwin-thread-multi-2level/CORE/config.h', needed by `Makefile'.  Stop.
            raise ConanInvalidConfiguration("Due to weird make error involving missing config.h file in sysroot")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    @contextlib.contextmanager
    def _build_context(self):
        if self.settings.compiler == "Visual Studio":
            with tools.vcvars(self):
                env = {
                    "AR": "{} lib".format(tools.microsoft.unix_path(self, self.deps_user_info["automake"].ar_lib)),
                    "CC": "{} cl -nologo".format(tools.microsoft.unix_path(self, self.deps_user_info["automake"].compile)),
                    "CXX": "{} cl -nologo".format(tools.microsoft.unix_path(self, self.deps_user_info["automake"].compile)),
                    "NM": "dumpbin -symbols",
                    "OBJDUMP": ":",
                    "RANLIB": ":",
                    "STRIP": ":",
                }
                with tools.environment_append(env):
                    yield
        else:
            yield

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        self._autotools.libs = []
        if self.settings.compiler == "Visual Studio":
            self._autotools.flags.append("-FS")
            self._autotools.cxx_flags.append("-EHsc")
        yes_no = lambda v: "yes" if v else "no"
        conf_args = [
            "--enable-shared={}".format(yes_no(self.options.shared)),
            "--enable-static={}".format(yes_no(not self.options.shared)),
            "CHECK_CFLAGS=' '",
            "CHECK_LIBS=' '",
            "CPPUNIT_CFLAGS='{}'".format(" ".join("-I{}".format(inc) for inc in self.deps_cpp_info["cppunit"].include_paths).replace("\\", "/")),
            "CPPUNIT_LIBS='{}'".format(" ".join(self.deps_cpp_info["cppunit"].libs)),
        ]
        self._autotools.configure(args=conf_args, configure_dir=self._source_subfolder)
        return self._autotools

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.patch(self, **patch)
        with self._build_context():
            autotools = self._configure_autotools()
            autotools.make()

    def package(self):
        self.copy("COPYING", src=self._source_subfolder, dst="licenses")
        with self._build_context():
            autotools = self._configure_autotools()
            # Avoid installing i18n + perl things in arch-dependent folders or in a `local` subfolder
            install_args = [
                "INSTALLARCHLIB={}".format(os.path.join(self.package_folder, "lib").replace("\\", "/")),
                "INSTALLSITEARCH={}".format(os.path.join(self.build_folder, "archlib").replace("\\", "/")),
                "INSTALLVENDORARCH={}".format(os.path.join(self.build_folder, "archlib").replace("\\", "/")),
                "INSTALLSITEBIN={}".format(os.path.join(self.package_folder, "bin").replace("\\", "/")),
                "INSTALLSITESCRIPT={}".format(os.path.join(self.package_folder, "bin").replace("\\", "/")),
                "INSTALLSITEMAN1DIR={}".format(os.path.join(self.build_folder, "share", "man", "man1").replace("\\", "/")),
                "INSTALLSITEMAN3DIR={}".format(os.path.join(self.build_folder, "share", "man", "man3").replace("\\", "/")),
            ]
            autotools.install(args=install_args)

        tools.files.rm(self, os.path.join(self.package_folder, "lib"), "*.la")
        tools.files.rm(self, os.path.join(self.package_folder, "lib"), "*.pod")
        for d in glob.glob(os.path.join(self.package_folder, "lib", "python*")):
            tools.files.rmdir(self, d)
        for d in glob.glob(os.path.join(self.package_folder, "lib", "*")):
            if os.path.isdir(d):
                tools.files.rmdir(self, d)
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.files.rmdir(self, os.path.join(self.package_folder, "Library"))

    def package_info(self):
        self.cpp_info.components["libsubunit"].libs = ["subunit"]
        self.cpp_info.components["libsubunit"].names["pkgconfig"] = "libsubunit"
        self.cpp_info.components["libcppunit_subunit"].libs = ["cppunit_subunit"]
        self.cpp_info.components["libcppunit_subunit"].requires = ["cppunit::cppunit"]
        self.cpp_info.components["libcppunit_subunit"].names["pkgconfig"] = "libcppunit_subunit"

        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bin_path))
        self.env_info.PATH.append(bin_path)
