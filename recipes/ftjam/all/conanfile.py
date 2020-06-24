from conans import AutoToolsBuildEnvironment, ConanFile, tools
from conans.errors import ConanInvalidConfiguration
import os


class FtjamConan(ConanFile):
    name = "ftjam"
    description = "Jam (ftjam) is a small open-source build tool that can be used as a replacement for Make."
    topics = ("conan", "ftjam", "build", "make")
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
        if self.settings.compiler == "Visual Studio":
            raise ConanInvalidConfiguration("ftjam does not work, built with Visual Studio")
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("ftjam-{}".format(self.version), self._source_subfolder)

    def build_requirements(self):
        if tools.os_info.is_windows and "CONAN_BASH_PATH" not in os.environ and \
                tools.os_info.detect_windows_subsystem() != "msys2":
            self.build_requires("msys2/20190524")
        if self.settings.compiler == "Visual Studio":
            self.build_requires("automake/1.16.2")
        if self.settings.os != "Windows":
            self.build_requires("bison/3.5.3")

    def _patch_sources(self):
        tools.replace_in_file(os.path.join(self._source_subfolder, "jamgram.c"),
                              "\n#line", "\n//#line")
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        self._autotools.libs = []
        # The configure MUST be run inside this directory
        with tools.chdir(os.path.join(self.build_folder, self._source_subfolder, "builds", "unix")):
            self._autotools.configure()
        return self._autotools

    def build(self):
        if self.settings.build_type != "Release":
            raise ConanInvalidConfiguration("This build_type is disabled in order to diminish the number of builds")
        if self.settings.compiler == "Visual Studio":
            if self.settings.compiler.runtime != "MT":
                raise ConanInvalidConfiguration("This runtime is disabled in order to diminish the number of builds")

        # toolset name of the system building ftjam
        jam_toolset = self._jam_toolset(self.settings.os, self.settings.compiler)
        autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        autotools.libs = []
        env = autotools.vars
        self._patch_sources()
        with tools.chdir(self._source_subfolder):
            if self.settings.compiler == "Visual Studio":
                autotools = AutoToolsBuildEnvironment(self)
                autotools.libs = []
                with tools.environment_append(env):
                    with tools.vcvars(self.settings):
                        self.run("nmake -f builds/win32-visualc.mk JAM_TOOLSET={}".format(jam_toolset))
            else:
                if self.settings.os == "Windows":
                    with tools.environment_append(env):
                        with tools.environment_append({"PATH": [os.getcwd()]}):
                            autotools.make(args=["JAM_TOOLSET={}".format(jam_toolset), "-f", "builds/win32-gcc.mk"])
                else:
                    autotools = self._configure_autotools()
                    autotools.make()

    def package(self):
        txt = tools.load(os.path.join(self._source_subfolder, "jam.c"))
        license_txt = txt[:txt.find("*/")+3]
        tools.save(os.path.join(self.package_folder, "licenses", "LICENSE"), license_txt)
        if self.settings.compiler == "Visual Studio":
            pass
        else:
            if self.settings.os == "Windows":
                self.copy("*.exe", src=os.path.join(self._source_subfolder, "bin.nt"), dst=os.path.join(self.package_folder, "bin"))
            else:
                with tools.chdir(self._source_subfolder):
                    autotools = self._configure_autotools()
                    autotools.install()

    def _jam_toolset(self, os, compiler):
        if compiler == "Visual Studio":
            return "VISUALC"
        if compiler == "intel":
            return "INTELC"
        if os == "Windows":
            return "MINGW"
        return None

    def package_id(self):
        del self.info.settings.build_type
        del self.info.settings.compiler

    def package_info(self):
        jam_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(jam_path))
        self.env_info.PATH.append(jam_path)

        jam_bin = os.path.join(jam_path, "jam")
        if self.settings.os == "Windows":
            jam_bin += ".exe"
        self.output.info("Setting JAM environment variable: {}".format(jam_bin))
        self.env_info.JAM.append(jam_bin)

        # toolset of the system using ftjam
        jam_toolset = self._jam_toolset(self.settings.os, self.settings.compiler)
        if jam_toolset:
            self.output.info("Setting JAM_TOOLSET environment variable: {}".format(jam_toolset))
            self.env_info.JAM_TOOLSET = jam_toolset
