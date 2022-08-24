import glob
import os
from conans import ConanFile, tools
from conan.errors import ConanInvalidConfiguration


class NamedTypeConan(ConanFile):
    name = "namedtype"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/joboccara/NamedType"
    description = "Implementation of strong types in C++"
    topics = ("strong types", "header-only")
    settings = "compiler"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = glob.glob("NamedType-*")[0]
        os.rename(extracted_dir, self._source_subfolder)

    @property
    def _minimum_cpp_standard(self):
        return 14

    @property
    def _minimum_compilers_version(self):
        return {
            "Visual Studio": "15",
            "gcc": "5",
            "clang": "3.4",
            "apple-clang": "5.1",
        }

    def configure(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, self._minimum_cpp_standard)
        min_version = self._minimum_compilers_version.get(str(self.settings.compiler))
        if not min_version:
            self.output.warn("{} recipe lacks information about the {} compiler support.".format(
                self.name, self.settings.compiler))
        else:
            if tools.Version(self.settings.compiler.version) < min_version:
                raise ConanInvalidConfiguration("{} requires C++{} support. The current compiler {} {} does not support it.".format(
                    self.name, self._minimum_cpp_standard, self.settings.compiler, self.settings.compiler.version))

    def package(self):
        if self.version == "20190324":
            self.copy("*.hpp", dst=os.path.join("include", "NamedType"), src=self._source_subfolder)
        else:
            self.copy("*.hpp", dst="include", src=os.path.join(self._source_subfolder, 'include'))
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)

    def package_info(self):
        if self.version == "20190324":
            self.cpp_info.includedirs.append(os.path.join("include", "NamedType"))

    def package_id(self):
        self.info.header_only()
