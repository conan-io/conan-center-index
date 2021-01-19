from conans import AutoToolsBuildEnvironment, ConanFile, tools
from conans.errors import ConanInvalidConfiguration
from contextlib import contextmanager
import glob
import os


class SubunitConan(ConanFile):
    name = "subunit"
    description = "A streaming protocol for test results"
    topics = "conan", "subunit", "streaming", "protocol", "test", "results"
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
    exports_sources = "patches/**"

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
            if self.settings.os == "Windows":
                raise ConanInvalidConfiguration("Cannot build shared subunit libraries on Windows")
        if self.settings.compiler == "apple-clang" and tools.Version(self.settings.compiler.version) < "10":
            # Complete error is:
            # make[2]: *** No rule to make target `/Applications/Xcode-9.4.app/Contents/Developer/Platforms/MacOSX.platform/Developer/SDKs/MacOSX10.13.sdk/System/Library/Perl/5.18/darwin-thread-multi-2level/CORE/config.h', needed by `Makefile'.  Stop.
            raise ConanInvalidConfiguration("Due to weird make error involving missing config.h file in sysroot")

    def requirements(self):
        self.requires("cppunit/1.15.1")

    def build_requirements(self):
        if tools.os_info.is_windows and not tools.get_env("CONAN_BASH_PATH"):
            self.build_requires("msys2/20200517")
        if self.settings.compiler == "Visual Studio":
            self.build_requires("automake/1.16.2")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("{}-{}".format(self.name, self.version), self._source_subfolder)

    @contextmanager
    def _build_context(self):
        env = {}
        if self.settings.compiler == "Visual Studio":
            with tools.vcvars(self.settings):
                env.update({
                    "AR": "{} lib".format(tools.unix_path(self.deps_user_info["automake"].ar_lib)),
                    "CC": "{} cl -nologo".format(tools.unix_path(self.deps_user_info["automake"].compile)),
                    "CXX": "{} cl -nologo".format(tools.unix_path(self.deps_user_info["automake"].compile)),
                    "NM": "dumpbin -symbols",
                    "OBJDUMP": ":",
                    "RANLIB": ":",
                    "STRIP": ":",
                })
                with tools.environment_append(env):
                    yield
        else:
            with tools.environment_append(env):
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
        with self._build_context():
            autotools = self._configure_autotools()
            autotools.make()

    def package(self):
        self.copy("COPYING", src=self._source_subfolder, dst="licenses")
        with self._build_context():
            autotools = self._configure_autotools()
            autotools.install()

        os.unlink(os.path.join(self.package_folder, "lib", "libcppunit_subunit.la"))
        os.unlink(os.path.join(self.package_folder, "lib", "libsubunit.la"))
        for d in glob.glob(os.path.join(self.package_folder, "lib", "python*")):
            tools.rmdir(d)
        for d in glob.glob(os.path.join(self.package_folder, "lib", "*")):
            if os.path.isdir(d):
                tools.rmdir(d)
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "Library"))

    def package_info(self):
        self.cpp_info.components["libsubunit"].libs = ["subunit"]
        self.cpp_info.components["libsubunit"].names["pkgconfig"] = "libsubunit"
        self.cpp_info.components["libcppunit_subunit"].libs = ["cppunit_subunit"]
        self.cpp_info.components["libcppunit_subunit"].requires = ["cppunit::cppunit"]
        self.cpp_info.components["libcppunit_subunit"].names["pkgconfig"] = "libcppunit_subunit"

        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bin_path))
        self.env_info.PATH.append(bin_path)
