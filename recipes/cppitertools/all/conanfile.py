import os
from conans import ConanFile, tools

required_conan_version = ">=1.28.0"


class CppItertoolsConan(ConanFile):
    name = "cppitertools"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/ryanhaining/cppitertools"
    description = "Implementation of python itertools and builtin iteration functions for C++17"
    topics = ("cpp17", "span", "span-implementations")
    license = "BSD-2-Clause"
    no_copy_source = True

    settings = "os", "arch", "compiler", "build_type"
    options = {'zip_longest': [True, False]}
    default_options = {'zip_longest': False}

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def validate(self):
        # Requires C++17
        minimal_version = {
            "Visual Studio": "16",
            "gcc": "7.3",
            "clang": "6.0",
            "apple-clang": "10.0"
        }
        compiler = str(self.settings.compiler)
        compiler_version = tools.Version(self.settings.compiler.version)

        if compiler not in minimal_version:
            self.output.info("{} requires a compiler that supports at least C++17".format(self.name, min))
            return

        # Exclude compilers not supported by cppitertools
        if compiler_version < minimal_version[compiler]:
            raise ConanInvalidConfiguration("{} requires a compiler that supports at least C++17. {} {} is not".format(
                self.name, compiler, tools.Version(self.settings.compiler.version.value)))

    def requirements(self):
        if self.options.zip_longest:
            self.requires('boost/1.75.0')

    def package(self):
        self.copy("*.hpp", dst="include/cppitertools", src=os.path.join(self._source_subfolder), excludes=('examples/**', 'test/**'))
        self.copy("LICENSE.md", dst="licenses", src=self._source_subfolder)

    def package_id(self):
        self.info.header_only()
