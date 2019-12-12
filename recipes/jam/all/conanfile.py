from conans import AutoToolsBuildEnvironment, ConanFile, tools
from contextlib import contextmanager
import os


class JamConan(ConanFile):
    name = "jam"
    description = "Jam is a small open-source build tool that can be used as a replacement for Make."
    topics = ("conan", "jam", "build", "make")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.freetype.org/jam/"
    license = "BSD-3-Clause"
    exports_sources = "patches/*"
    settings = "os", "arch", "compiler", "build_type"

    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("ftjam-{}".format(self.version), self._source_subfolder)

    def build_requirements(self):
        if tools.os_info.is_windows and "CONAN_BASH_PATH" not in os.environ and \
                not tools.os_info.detect_windows_subsystem() != "msys2":
            self.build_requires("msys2/20190524")
        self.build_requires("bison/3.5.3")

    def _patch_sources(self):
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)

    @contextmanager
    def _build_context(self):
        if self.settings.compiler == "Visual Studio":
                with tools.vcvars(self.settings):
                    yield
        else:
            # Use autotools to get the build environment variables. Do not use self._configure_autotools!
            autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
            with tools.environment_append(autotools.vars):
                with tools.environment_append({"CCFLAGS": os.environ["CFLAGS"]}):
                    yield

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        # The configure MUST be run inside this directory
        with tools.chdir(os.path.join(self.build_folder, self._source_subfolder, "builds", "unix")):
            self._autotools.configure()
        return self._autotools

    def build(self):
        self._patch_sources()
        with self._build_context():
            with tools.chdir(self._source_subfolder):
                autotools = self._configure_autotools()
                autotools.make()

    def package(self):
        txt = tools.load(os.path.join(self._source_subfolder, "jam.c"))
        license_txt = txt[:txt.find("*/")+3]
        tools.save(os.path.join(self.package_folder, "licenses", "LICENSE"), license_txt)
        with tools.chdir(self._source_subfolder):
            autotools = self._configure_autotools()
            autotools.install()

    def package_info(self):
        jam_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH env var with : {}".format(jam_path))
        self.env_info.PATH.append(jam_path)

        jam_bin = os.path.join(jam_path, "jam")
        if self.settings.os == "Windows":
            jam_bin += ".exe"
        self.output.info("Setting JAM env var to {}".format(jam_bin))
        self.env_info.JAM.append(jam_bin)
