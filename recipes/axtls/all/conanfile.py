from conans import ConanFile, CMake, tools
import os
import shutil

class AxtlsConan(ConanFile):
    name = "axtls"
    license = "GPL-3.0"
    author = "Starkov Kirill <k.starkov@dssl.ru>"
    url = "dssl.ru"
    description = "The axTLS embedded SSL project is a library designed for platforms with small memory requirements"
    topics = ("ssl", "crypto", "openssl")
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False]}
    default_options = {"shared": True}
    exports_sources = [
        "osx10_compat.patch",
        "SNI.patch",

        "CMakeLists.txt",
        "win.patch",
        "win_config.h"
    ]

    @property
    def _source_subfolder(self):
        return os.path.join(self.source_folder, "axtls-code")

    @property
    def _build_subfolder(self):
        return os.path.join(self.source_folder, "build")

    def _make(self, args):
        if tools.os_info.is_windows:
            cmake = CMake(self, generator="Ninja")
            cmake.verbose = True
            cmake.build(build_dir=self._build_subfolder)
        else:
            self.run("make -C {source} {args}".format(source = self._source_subfolder, args = args))

    def _configure(self):
        if tools.os_info.is_windows:
            cmake = CMake(self, generator="Ninja")
            cmake.verbose = True
            cmake.configure(source_folder=self._source_subfolder, build_folder=self._build_subfolder)
        else:
            prefix = tools.unix_path(self.package_folder)

            shutil.copyfile(
                os.path.join(self._source_subfolder,"config", "linuxconfig"),
                os.path.join(self._source_subfolder,"config", ".config"))

            options = [
                "CONFIG_SSL_SNI=y",
            ]

            tools.replace_in_file(os.path.join(self._source_subfolder, "config", ".config"),
                "PREFIX=\"/usr/local\"",
                "PREFIX=\"{prefix}\"\n{options}".format(prefix = prefix, options = "\n".join(options)))

            if tools.is_apple_os(self.settings.os):
                tools.replace_in_file(os.path.join(self._source_subfolder, "config", "makefile.conf"),
                                      "LDSHARED = -shared",
                                      "LDSHARED = -dynamiclib")
            self._make("oldconfig")

    def _install(self):
        if tools.os_info.is_windows:
            cmake = CMake(self, generator="Ninja")
            cmake.verbose = True
            cmake.install(build_dir=self._build_subfolder)
        else:
            self._make("install")

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        # download sources
        tools.get(**self.conan_data["sources"][self.version])

        # check recipe conistency
        tools.check_with_algorithm_sum("sha1", "osx10_compat.patch", "e211d33b1198e932ac251a811b783583ce1ec278")
        tools.check_with_algorithm_sum("sha1", "SNI.patch",          "13ec4af9bab09839a4cd6fc0d7c935749cba04f9")

        tools.check_with_algorithm_sum("sha1", "CMakeLists.txt",     "884441e52e8d848fbbca5c9fa0a3d04244e7a049")
        tools.check_with_algorithm_sum("sha1", "win_config.h",       "484eb1f669576af2793614482ba33b8bce40e0db")
        tools.check_with_algorithm_sum("sha1", "win.patch",          "5c9364fc147eef1e60d004a0ea565c10c5d1219c")

        # apply patches
        tools.patch(base_path = self._source_subfolder, patch_file = "SNI.patch", strip = 1)

        if tools.is_apple_os(self.settings.os):
            tools.patch(base_path = self._source_subfolder, patch_file = "osx10_compat.patch", strip = 1)

        if tools.os_info.is_windows:
            shutil.copyfile(
                os.path.join(self.source_folder, "CMakeLists.txt"),
                os.path.join(self._source_subfolder, "CMakeLists.txt"))
            shutil.copyfile(
                os.path.join(self.source_folder, "win_config.h"),
                os.path.join(self._source_subfolder, "config", "config.h"))
            tools.patch(base_path = self._source_subfolder, patch_file = "win.patch", strip = 1)

    def build(self):
        self._configure()
        self._make("-j%d" % tools.cpu_count())

    def package(self):
        self._install()

    def package_info(self):
        self.env_info.CMAKE_PREFIX_PATH.append(self.package_folder)
        self.cpp_info.libs = ["axtls"]
