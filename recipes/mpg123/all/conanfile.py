from conans import AutoToolsBuildEnvironment, CMake, ConanFile, tools
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.33.0"


class Mpg123Conan(ConanFile):
    name = "mpg123"
    description = "Fast console MPEG Audio Player and decoder library"
    topics = ("conan", "mpg123", "mpeg", "audio", "player", "decoder")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://mpg123.org/"
    license = "LGPL-2.1-or-later", "GPL-2.0-or-later"
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "flexible_resampling": [True, False],
        "network": [True, False],
        "icy": [True, False],
        "id3v2": [True, False],
        "ieeefloat": [True, False],
        "layer1": [True, False],
        "layer2": [True, False],
        "layer3": [True, False],
        "moreinfo": [True, False],
        "seektable": "ANY",
        "module": ["dummy", "libalsa", "tinyalsa", "win32"],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "flexible_resampling": True,
        "network": True,
        "icy": True,
        "id3v2": True,
        "ieeefloat": True,
        "layer1": True,
        "layer2": True,
        "layer3": True,
        "moreinfo": True,
        "seektable": "1000",
        "module": "dummy",
    }
    exports_sources = "CMakeLists.txt", "patches/**"
    generators = "cmake", "pkg_config", "cmake_find_package"

    _autotools = None
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        if self.options.module == "libalsa":
            self.requires("libalsa/1.2.4")
        if self.options.module == "tinyalsa":
            self.requires("tinyalsa/1.1.1")

    def validate(self):
        try:
            int(self.options.seektable)
        except ValueError:
            raise ConanInvalidConfiguration("seektable must be an integer")
        if self.settings.os != "Windows":
            if self.options.module == "win32":
                raise ConanInvalidConfiguration("win32 is an invalid module for non-Windows os'es")

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def build_requirements(self):
        self.build_requires("pkgconf/1.7.4")
        if self.settings.arch in ["x86", "x86_64"]:
            self.build_requires("yasm/1.3.0")
        if self._settings_build.os == "Windows" and self.settings.compiler != "Visual Studio" and \
           not tools.get_env("CONAN_BASH_PATH"):
            self.build_requires("msys2/cci.latest")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    @property
    def _audio_module(self):
        return {
            "libalsa": "alsa",
        }.get(str(self.options.module), str(self.options.module))

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        yes_no = lambda v: "yes" if v else "no"
        conf_args = [
            "--enable-moreinfo={}".format(yes_no(self.options.moreinfo)),
            "--enable-network={}".format(yes_no(self.options.network)),
            "--enable-ntom={}".format(yes_no(self.options.flexible_resampling)),
            "--enable-icy={}".format(yes_no(self.options.icy)),
            "--enable-id3v2={}".format(yes_no(self.options.id3v2)),
            "--enable-ieeefloat={}".format(yes_no(self.options.ieeefloat)),
            "--enable-layer1={}".format(yes_no(self.options.layer1)),
            "--enable-layer2={}".format(yes_no(self.options.layer2)),
            "--enable-layer3={}".format(yes_no(self.options.layer3)),
            "--with-audio={}".format(self._audio_module),
            "--with-default-audio={}".format(self._audio_module),
            "--with-seektable={}".format(self.options.seektable),
            "--enable-modules=no",
            "--enable-shared={}".format(yes_no(self.options.shared)),
            "--enable-static={}".format(yes_no(not self.options.shared)),
        ]
        self._autotools.configure(args=conf_args, configure_dir=self._source_subfolder)
        return self._autotools

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["NO_MOREINFO"] = not self.options.moreinfo
        self._cmake.definitions["NETWORK"] = self.options.network
        self._cmake.definitions["NO_NTOM"] = not self.options.flexible_resampling
        self._cmake.definitions["NO_ICY"] = not self.options.icy
        self._cmake.definitions["NO_ID3V2"] = not self.options.id3v2
        self._cmake.definitions["IEEE_FLOAT"] = self.options.ieeefloat
        self._cmake.definitions["NO_LAYER1"] = not self.options.layer1
        self._cmake.definitions["NO_LAYER2"] = not self.options.layer2
        self._cmake.definitions["NO_LAYER3"] = not self.options.layer3
        self._cmake.definitions["USE_MODULES"] = False
        self._cmake.definitions["CHECK_MODULES"] = self._audio_module
        self._cmake.definitions["WITH_SEEKTABLE"] = self.options.seektable
        self._cmake.verbose = True
        self._cmake.parallel = False
        self._cmake.configure()
        return self._cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.patch(self, **patch)
        if self.settings.compiler == "Visual Studio":
            cmake = self._configure_cmake()
            cmake.build()
        else:
            autotools = self._configure_autotools()
            autotools.make()

    def package(self):
        self.copy("COPYING", src=self._source_subfolder, dst="licenses")
        if self.settings.compiler == "Visual Studio":
            cmake = self._configure_cmake()
            cmake.install()
            tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        else:
            autotools = self._configure_autotools()
            autotools.install()
            tools.files.rm(self, os.path.join(self.package_folder, "lib"), "*.la")
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.files.rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.filenames["cmake_find_package"] = "mpg123"
        self.cpp_info.filenames["cmake_find_package_multi"] = "mpg123"
        self.cpp_info.names["cmake_find_package"] = "MPG123"
        self.cpp_info.names["cmake_find_package_multi"] = "MPG123"

        self.cpp_info.components["libmpg123"].libs = ["mpg123"]
        self.cpp_info.components["libmpg123"].names["pkg_config"] = "libmpg123"
        if self.settings.os == "Windows" and self.options.shared:
            self.cpp_info.components["libmpg123"].defines.append("LINK_MPG123_DLL")

        self.cpp_info.components["libout123"].libs = ["out123"]
        self.cpp_info.components["libout123"].names["pkg_config"] = "libout123"
        self.cpp_info.components["libout123"].requires = ["libmpg123"]

        self.cpp_info.components["libsyn123"].libs = ["syn123"]
        self.cpp_info.components["libsyn123"].names["pkg_config"] = "libsyn123"
        self.cpp_info.components["libsyn123"].requires = ["libmpg123"]

        if self.settings.os == "Linux":
            self.cpp_info.components["libmpg123"].system_libs = ["m"]
        elif self.settings.os == "Windows":
            self.cpp_info.components["libmpg123"].system_libs = ["shlwapi"]

        if self.options.module == "libalsa":
            self.cpp_info.components["libout123"].requires.append("libalsa::libalsa")
        if self.options.module == "tinyalsa":
            self.cpp_info.components["libout123"].requires.append("tinyalsa::tinyalsa")
        if self.options.module == "win32":
            self.cpp_info.components["libout123"].system_libs.append("winmm")

        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bin_path))
        self.env_info.PATH.append(bin_path)
