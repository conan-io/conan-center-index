from from conan import ConanFile, tools
from conans import CMake
import os

required_conan_version = ">=1.33.0"


class LemonConan(ConanFile):
    name = "lemon"
    description = "The Lemon program reads a grammar of the input language and emits C-code to implement a parser for that language."
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://sqlite.org/lemon.html"
    topics = ("conan", "lemon", "grammar", "lexer", "lalr", "parser", "generator", "sqlite")
    license = "Unlicense"
    exports_sources = "CMakeLists.txt", "patches/**"
    settings = "os", "compiler", "arch", "build_type"
    generators = "cmake"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    _cmake = None

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.configure()
        return self._cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def _extract_license_text(self):
        header = tools.load(os.path.join(self._source_subfolder, "tool", "lempar.c"))
        return "\n".join(line.strip(" \n*") for line in header[3:header.find("*******", 1)].splitlines())

    def package(self):
        tools.save(os.path.join(self.package_folder, "licenses", "LICENSE"), self._extract_license_text())
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bin_path))
        self.env_info.PATH.append(bin_path)
