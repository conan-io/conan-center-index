from conans import ConanFile, tools, AutoToolsBuildEnvironment, CMake
import os
import glob


class RagelConan(ConanFile):
    name = "ragel"
    description = "Ragel compiles executable finite state machines from regular languages"
    homepage = "http://www.colm.net/open-source/ragel"
    url = "https://github.com/conan-io/conan-center-index"
    license = "GPL-2.0-or-later"
    topics = ("conan", "ragel", "FSM", "regex", "fsm-compiler")
    exports_sources = ["CMakeLists.txt", "config.h", "patches/*"]
    generators = "cmake"

    settings = "os", "arch", "compiler"

    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = glob.glob(self.name + "-*/")[0]
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_autotools(self):
        if not self._autotools:
            self._autotools = AutoToolsBuildEnvironment(self)
            self._autotools.configure(configure_dir=self._source_subfolder)
        return self._autotools

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.configure()
        return cmake

    def build(self):
        for patch in self.conan_data["patches"].get(self.version, []):
            tools.patch(**patch)

        if self.settings.os == "Windows":
            cmake = self._configure_cmake()
            cmake.build()
        else:
            autotools = self._configure_autotools()
            autotools.make()

    def package(self):
        self.copy(pattern="COPYING", dst="licenses", src=self._source_subfolder)
        self.copy(pattern="CREDITS", dst="licenses", src=self._source_subfolder)
        if self.settings.os == "Windows":
            cmake = self._configure_cmake()
            cmake.install()
        else:
            autotools = self._configure_autotools()
            autotools.install()
        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_id(self):
        del self.info.settings.compiler

    def package_info(self):
        self.env_info.RAGEL_ROOT = self.package_folder
        bindir = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bindir))
        self.env_info.PATH.append(bindir)
