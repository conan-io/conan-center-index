from conans import ConanFile, AutoToolsBuildEnvironment, tools
from conan.errors import ConanInvalidConfiguration
import os
import textwrap

required_conan_version = ">=1.33.0"

class BreakpadConan(ConanFile):
    name = "breakpad"
    description = "A set of client and server components which implement a crash-reporting system"
    topics = ["crash", "report", "breakpad"]
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://chromium.googlesource.com/breakpad/breakpad/"
    settings = "os", "compiler", "build_type", "arch"
    provides = "breakpad"
    exports_sources = "patches/**"
    options = {
        "fPIC": [True, False]
    }
    default_options = {
        "fPIC": True
    }
    _env_build = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def validate(self):
        if self.settings.os != "Linux":
            raise ConanInvalidConfiguration("Breakpad can only be built on Linux. For other OSs check sentry-breakpad")

    def requirements(self):
        self.requires("linux-syscall-support/cci.20200813")

    def _configure_autotools(self):
        if not self._env_build:
            self._env_build = AutoToolsBuildEnvironment(self)
            self._env_build.configure(configure_dir=self._source_subfolder)
        return self._env_build

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], destination=self._source_subfolder, strip_root=True)

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        env_build = self._configure_autotools()
        env_build.make()

    def package(self):
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")
        env_build = self._configure_autotools()
        env_build.install()
        tools.rmdir(os.path.join(self.package_folder, "share"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info( self ):
        self.cpp_info.components["libbreakpad"].libs = ["breakpad"]
        self.cpp_info.components["libbreakpad"].includedirs.append(os.path.join("include", "breakpad"))
        self.cpp_info.components["libbreakpad"].names["pkg_config"] = "breakpad"

        self.cpp_info.components["client"].libs = ["breakpad_client"]
        self.cpp_info.components["client"].includedirs.append(os.path.join("include", "breakpad"))
        self.cpp_info.components["client"].names["pkg_config"] = "breakpad-client"


        self.cpp_info.components["libbreakpad"].system_libs.append("pthread")
        self.cpp_info.components["libbreakpad"].requires.append("linux-syscall-support::linux-syscall-support")

        self.cpp_info.components["client"].system_libs.append("pthread")
        self.cpp_info.components["client"].requires.append("linux-syscall-support::linux-syscall-support")

        bindir = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bindir))
        self.env_info.PATH.append(bindir)
