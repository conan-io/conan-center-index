from conan.errors import ConanInvalidConfiguration
from conans import ConanFile, tools
import os

required_conan_version = ">=1.33.0"

class CTPGConan(ConanFile):
    name = "ctpg"
    license = "MIT"
    description = (
        "Compile Time Parser Generator is a C++ single header library which takes a language description as a C++ code "
        "and turns it into a LR1 table parser with a deterministic finite automaton lexical analyzer, all in compile time."
    )
    topics = ("regex", "parser", "grammar", "compile-time")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/peter-winter/ctpg"
    settings = "compiler",
    no_copy_source = True

    _compiler_required_cpp17 = {
        "Visual Studio": "16",
        "gcc": "8",
        "clang": "12",
        "apple-clang": "12.0",
    }

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def validate(self):
        ## TODO: In ctpg<=1.3.5, Visual Studio C++ failed to compile ctpg with "error MSB6006: "CL.exe" exited with code -1073741571."
        if self.settings.compiler == "Visual Studio":
            raise ConanInvalidConfiguration("{} does not support Visual Studio currently.".format(self.name))

        if self.settings.get_safe("compiler.cppstd"):
            tools.build.check_min_cppstd(self, self, "17")

        minimum_version = self._compiler_required_cpp17.get(str(self.settings.compiler), False)
        if minimum_version:
            if tools.scm.Version(self, self.settings.compiler.version) < minimum_version:
                raise ConanInvalidConfiguration("{} requires C++17, which your compiler does not support.".format(self.name))
        else:
            self.output.warn("{} requires C++17. Your compiler is unknown. Assuming it supports C++17.".format(self.name))

    def package_id(self):
        self.info.header_only()

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version], destination=self._source_subfolder, strip_root=True)

    def package(self):
        self.copy("LICENSE*", "licenses", self._source_subfolder)
        if tools.scm.Version(self, self.version) >= "1.3.7":
            self.copy("ctpg.hpp",
                os.path.join("include", "ctpg"), 
                os.path.join(self._source_subfolder, "include", "ctpg"))
        else:
            self.copy("ctpg.hpp", "include", os.path.join(self._source_subfolder, "include"))
