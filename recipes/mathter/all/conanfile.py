from conans import ConanFile, tools
from conan.errors import ConanInvalidConfiguration
import os

class MathterConan(ConanFile):
    name = "mathter"
    license = "MIT"
    homepage = "https://github.com/petiaccja/Mathter"
    url = "https://github.com/conan-io/conan-center-index/"
    description = "Powerful 3D math and small-matrix linear algebra library for games and science."
    topics = ("game-dev", "linear-algebra", "vector-math", "matrix-library")
    no_copy_source = True
    settings = "compiler"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _compilers_minimum_version(self):
        return {
            "apple-clang": 10,
            "clang": 6,
            "gcc": 7,
            "Visual Studio": 16,
        }

    def configure(self):
        if self.settings.compiler.cppstd:
            tools.build.check_min_cppstd(self, "17")

        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version:
            if tools.scm.Version(self.settings.compiler.version) < minimum_version:
                raise ConanInvalidConfiguration("mathter requires C++17, which your compiler does not support.")
        else:
            self.output.warn("mathter requires C++17. Your compiler is unknown. Assuming it supports C++17.")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version])
        os.rename("Mathter-" + self.version, self._source_subfolder)
            
    def package(self):
        self.copy("*.hpp", dst=os.path.join("include", "Mathter"), src=os.path.join(self._source_subfolder, "Mathter"))
        self.copy("*.natvis", dst=os.path.join("include", "Mathter"), src=os.path.join(self._source_subfolder, "Mathter"))
        self.copy("LICENCE", dst="licenses", src=self._source_subfolder)

    def package_id(self):
        self.info.header_only()
