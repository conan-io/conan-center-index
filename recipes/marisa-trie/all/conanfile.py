import os
from conans import ConanFile, tools, AutoToolsBuildEnvironment


class MarisaTrieConan(ConanFile):
    name = "marisa-trie"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/s-yata/marisa-trie"
    description = "Matching Algorithm with Recursively Implemented StorAge "
    license = ("BSD-2-Clause", "LGPL-2.1")
    topics = ("algorithm", "dictionary", "marisa")
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    exports_sources = "CMakeLists.txt"

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
        self.build_requires("libtool/2.4.6")
        self.build_requires("automake/1.16.3")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self.run("{} -fiv".format(tools.get_env("AUTORECONF")), win_bash=tools.os_info.is_windows)
        self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        if self.settings.compiler == "Visual Studio":
            self._autotools.flags.append("-FS")
        conf_args = [
            ("--enable-shared" if self.options.shared else "--enable-static"),
            ("--disable-static" if self.options.shared else "--disable-shared"),
            ("--with-pic" if self.options.get_safe("fPIC") or self.options.shared else "--without-pic"),
        ]
        self._autotools.configure(args=conf_args)
        return self._autotools

    def build(self):
        with tools.chdir(self._source_subfolder):
            autotools = self._configure_autotools()
            autotools.make()

    def package(self):
        self.copy("COPYING.md", src=self._source_subfolder, dst="licenses")
        with tools.chdir(self._source_subfolder):
            autotools = self._configure_autotools()
            autotools.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.remove_files_by_mask(os.path.join(self.package_folder, "lib"), "*.la")

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "marisa"
        self.cpp_info.names["cmake_find_package_multi"] = "marisa"
        self.cpp_info.names["pkgconfig"] = "marisa"
        self.cpp_info.libs = ["marisa"]
        if self.settings.os == "Linux":
            self.cpp_info.system_libs = ["m"]

        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH env var with : {}".format(bin_path))
        self.env_info.PATH.append(bin_path)
