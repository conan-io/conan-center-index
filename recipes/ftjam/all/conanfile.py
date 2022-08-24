from conans import AutoToolsBuildEnvironment, ConanFile, tools
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.33.0"


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
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def validate(self):
        if self.settings.compiler == "Visual Studio":
            raise ConanInvalidConfiguration("ftjam doesn't build with Visual Studio yet")
        if hasattr(self, "settings_build") and tools.cross_building(self):
            raise ConanInvalidConfiguration("ftjam can't be cross-built")

    def package_id(self):
        del self.info.settings.compiler

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def build_requirements(self):
        if self._settings_build.os == "Windows" and not tools.get_env("CONAN_BASH_PATH"):
            self.build_requires("msys2/cci.latest")
        if self.settings.compiler == "Visual Studio":
            self.build_requires("automake/1.16.2")
        if self.settings.os != "Windows":
            self.build_requires("bison/3.7.1")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        tools.replace_in_file(os.path.join(self._source_subfolder, "jamgram.c"),
                              "\n#line", "\n//#line")

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
        self._patch_sources()
        with tools.chdir(self._source_subfolder):
            if self.settings.os == "Windows":
                # toolset name of the system building ftjam
                jam_toolset = self._jam_toolset(self.settings.os, self.settings.compiler)
                autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
                autotools.libs = []
                env = autotools.vars
                with tools.environment_append(env):
                    if self.settings.compiler == "Visual Studio":
                        with tools.vcvars(self.settings):
                            self.run("nmake -f builds/win32-visualc.mk JAM_TOOLSET={}".format(jam_toolset))
                    else:
                        with tools.environment_append({"PATH": [os.getcwd()]}):
                            autotools.make(args=["JAM_TOOLSET={}".format(jam_toolset), "-f", "builds/win32-gcc.mk"])
            else:
                autotools = self._configure_autotools()
                autotools.make()

    def package(self):
        txt = tools.load(os.path.join(self._source_subfolder, "jam.c"))
        license_txt = txt[:txt.find("*/")+3]
        tools.save(os.path.join(self.package_folder, "licenses", "LICENSE"), license_txt)
        if self.settings.os == "Windows":
            if self.settings.compiler == "Visual Studio":
                pass
            else:
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

    def package_info(self):
        jam_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(jam_path))
        self.env_info.PATH.append(jam_path)

        jam_bin = os.path.join(jam_path, "jam")
        if self.settings.os == "Windows":
            jam_bin += ".exe"
        self.output.info("Setting JAM environment variable: {}".format(jam_bin))
        self.env_info.JAM = jam_bin

        # toolset of the system using ftjam
        jam_toolset = self._jam_toolset(self.settings.os, self.settings.compiler)
        if jam_toolset:
            self.output.info("Setting JAM_TOOLSET environment variable: {}".format(jam_toolset))
            self.env_info.JAM_TOOLSET = jam_toolset
