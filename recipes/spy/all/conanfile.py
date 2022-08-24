import os
from conan import ConanFile, tools$
from conan.errors import ConanInvalidConfiguration

class SpyConan(ConanFile):
    name = "spy"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://jfalcou.github.io/spy/"
    description = "C++ 17 for constexpr-proof detection and classification of informations about OS, compiler, etc..."
    topics = ("c++17", "config", "metaprogramming")
    settings = "compiler"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "7.4",
            "Visual Studio": "15.7",
            "clang": "6",
            "apple-clang": "10",
        }

    def configure(self):
        if self.settings.compiler.cppstd:
            tools.build.check_min_cppstd(self, 17)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version:
            if tools.scm.Version(self.settings.compiler.version) < minimum_version:
                raise ConanInvalidConfiguration("Spy requires C++17, which your compiler does not support.")
        else:
            self.output.warn("Spy requires C++17. Your compiler is unknown. Assuming it supports C++17.")

    def package_id(self):
        self.info.header_only()

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def package(self):
        self.copy("LICENSE.md", dst="licenses", src=self._source_subfolder)
        self.copy("*", dst= "include", src=os.path.join(self._source_subfolder, "include"))
