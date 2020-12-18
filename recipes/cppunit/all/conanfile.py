from conans import AutoToolsBuildEnvironment, ConanFile, tools
from contextlib import contextmanager
import os


class CppunitConan(ConanFile):
    name = "cppunit"
    description = "CppUnit is the C++ port of the famous JUnit framework for unit testing. Test output is in XML for automatic testing and GUI based for supervised tests."
    topics = ("conan", "cppunit", "unit-test", "tdd")
    license = " LGPL-2.1-or-later"
    homepage = "https://freedesktop.org/wiki/Software/cppunit/"
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
    generators = "pkg_config"

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
        if self.settings.compiler == "Visual Studio":
            with tools.vcvars(self.settings):
                env = {
                    "AR": "{} lib".format(tools.unix_path(self.deps_user_info["automake"].ar_lib)),
                    "CC": "{} cl -nologo".format(tools.unix_path(self.deps_user_info["automake"].compile)),
                    "CXX": "{} cl -nologo".format(tools.unix_path(self.deps_user_info["automake"].compile)),
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
        if self.settings.os == "Windows" and self.options.shared:
            self._autotools.defines.append("CPPUNIT_BUILD_DLL")
        if self.settings.compiler == "Visual Studio":
            self._autotools.flags.append("-FS")
            self._autotools.cxx_flags.append("-EHsc")
        yes_no = lambda v: "yes" if v else "no"
        conf_args = [
            "--enable-shared={}".format(yes_no(self.options.shared)),
            "--enable-static={}".format(yes_no(not self.options.shared)),
            "--enable-debug={}".format(yes_no(self.settings.build_type == "Debug")),
            "--enable-doxygen=no",
            "--enable-dot=no",
            "--enable-werror=no",
            "--enable-html-docs=no",
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

        if self.settings.compiler == "Visual Studio" and self.options.shared:
            os.rename(os.path.join(self.package_folder, "lib", "cppunit.dll.lib"),
                      os.path.join(self.package_folder, "lib", "cppunit.lib"))

        os.unlink(os.path.join(self.package_folder, "lib", "libcppunit.la"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.libs = ["cppunit"]
        if not self.options.shared:
            stdlib = tools.stdcpp_library(self)
            if stdlib:
                self.cpp_info.system_libs.append(stdlib)
            if self.settings.os == "Linux":
                self.cpp_info.system_libs.append("dl")
        if self.options.shared and self.settings.os == "Windows":
            self.cpp_info.defines.append("CPPUNIT_DLL")
        self.cpp_info.filenames["pkg_config"] = "cppunit"
