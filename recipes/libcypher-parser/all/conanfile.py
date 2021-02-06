from conans import ConanFile, AutoToolsBuildEnvironment, tools
from conans.errors import ConanInvalidConfiguration
import os

class LibcypherparserConan(ConanFile):
    name = "libcypher-parser"
    description = "A parser library and validation (lint) tool for Cypher, the graph query language"
    license = "Apache-2.0"
    topics = ("conan", "cypher", "parser")
    homepage = "https://github.com/cleishm/libcypher-parser"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "fPIC": [True, False],
    }
    default_options = {
        "fPIC": True,
    }
    build_requires = "peg/0.1.18@"
    
    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename(self.name + "-" + self.version, self._source_subfolder)

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        args = []
        self.run(os.path.join(self._source_subfolder, "autogen.sh"))
        self._autotools.configure(configure_dir=self._source_subfolder, args=args)
        return self._autotools

    def build(self):
        autotools = self._configure_autotools()
        workdir = self._source_subfolder
        tools.replace_in_file(os.path.join(os.path.abspath(self._source_subfolder), "..", "linter", "src", "Makefile"), "$(INCLUDES)", "$(INCLUDES) -I../../lib/src")
        autotools.make(target="check")

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        autotools = self._configure_autotools()
        autotools.install()

        tools.rmdir(os.path.join(self.package_folder, 'share'))

        os.unlink(os.path.join(self.package_folder, "lib", "libcypher-parser.la"))
        os.unlink(os.path.join(self.package_folder, "lib", "pkgconfig", "cypher-parser.pc"))

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "cypher-parser"
        self.cpp_info.names["cmake_find_package_multi"] = "cypher-parser"

        self.cpp_info.libs = tools.collect_libs(self)
