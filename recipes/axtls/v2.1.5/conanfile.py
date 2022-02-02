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
        "CMakeLists.txt",
        "win.patch",
        "win_config.h",
        "linux_config.h"
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
        tools.check_with_algorithm_sum("sha1", "CMakeLists.txt",     "f668b375dcaa4f54d4717f280c979af5beac9dd6")
        tools.check_with_algorithm_sum("sha1", "win_config.h",       "50ed49d199f6e5d37bdc30fa2c16980667312d0e")
        tools.check_with_algorithm_sum("sha1", "linux_config.h",     "9642cc945cf8da1819c865a48539f23fad7e6029")
        tools.check_with_algorithm_sum("sha1", "win.patch",          "3a97288876e0f979d440812d0ebf1d2fa7c9755c")

        if tools.os_info.is_windows:
            shutil.copyfile(
                os.path.join(self.source_folder, "CMakeLists.txt"),
                os.path.join(self._source_subfolder, "CMakeLists.txt"))
            shutil.copyfile(
                os.path.join(self.source_folder, "win_config.h"),
                os.path.join(self._source_subfolder, "config", "config.h"))
            tools.patch(base_path = self._source_subfolder, patch_file = "win.patch", strip = 1)
        elif tools.os_info.is_linux:
            prefix = tools.unix_path(self.package_folder)

            shutil.copyfile(
                os.path.join(self.source_folder, "linux_config.h"),
                os.path.join(self._source_subfolder, "config", "config.h"))

            tools.replace_in_file(os.path.join(self._source_subfolder, "config", ".config.h"),
                "PREFIX=\"/usr\"",
                "PREFIX=\"{prefix}\"\n{options}".format(prefix = prefix))

    def build(self):
        self._configure()
        self._make("-j%d" % tools.cpu_count())

    def package(self):
        self._install()

    def package_info(self):
        self.env_info.CMAKE_PREFIX_PATH.append(self.package_folder)
        self.cpp_info.libs = ["axtls"]
