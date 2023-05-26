import os
from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.files import get, copy, rename
from conan.tools.scm import Version
from conan.errors import ConanInvalidConfiguration

required_conan_version = ">=1.54.0"


class CppItertoolsConan(ConanFile):
    name = "cppitertools"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/ryanhaining/cppitertools"
    description = "Implementation of python itertools and builtin iteration functions for C++17"
    topics = ("cpp17", "iter", "itertools")
    license = "BSD-2-Clause"
    no_copy_source = True

    settings = "os", "arch", "compiler", "build_type"
    options = {'zip_longest': [True, False]}
    default_options = {'zip_longest': False}

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        get(self, **self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        rename(self, extracted_dir, self._source_subfolder)

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, 17)

        minimal_version = {
            "Visual Studio": "15",
            "msvc": "191",
            "gcc": "7",
            "clang": "5.0",
            "apple-clang": "9.1"
        }
        compiler = str(self.settings.compiler)
        compiler_version = Version(self.settings.compiler.version)

        if compiler not in minimal_version:
            self.output.info("{} requires a compiler that supports at least C++17".format(self.name))
            return

        # Exclude compilers not supported by cppitertools
        if compiler_version < minimal_version[compiler]:
            raise ConanInvalidConfiguration("{} requires a compiler that supports at least C++17. {} {} is not".format(
                self.name, compiler, Version(self.settings.compiler.version.value)))

    def requirements(self):
        if self.options.zip_longest:
            self.requires('boost/1.75.0')

    def package(self):
        copy(self, "*.hpp", src=os.path.join(self.source_folder, self._source_subfolder), dst=os.path.join(self.package_folder,"include", "cppitertools"), excludes=('examples/**', 'test/**'))
        copy(self, "LICENSE.md", src=os.path.join(self.source_folder, self._source_subfolder), dst=os.path.join(self.package_folder,"licenses"))

    def package_id(self):
        self.info.clear()
