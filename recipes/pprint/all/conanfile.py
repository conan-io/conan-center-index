from conans import ConanFile, tools
from conan.errors import ConanInvalidConfiguration
import os


class PprintConan(ConanFile):
    name = "pprint"
    homepage = "https://github.com/p-ranav/pprint"
    url = "https://github.com/conan-io/conan-center-index"
    description = "Pretty Printer for Modern C++"
    license = "MIT"
    settings = "os", "compiler"
    topics = ("conan", "pprint", "pretty", "printer")
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def configure(self):
        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, 17)

        min_compiler_version = {
            "gcc": 7,
            "clang": 7,
            "apple-clang": 10,
            "Visual Studio": 15,
        }.get(str(self.settings.compiler), None)

        if min_compiler_version:
            if tools.Version(self.settings.compiler.version) < min_compiler_version:
                raise ConanInvalidConfiguration("The compiler does not support c++17")
        else:
            self.output.warn("pprint needs a c++17 capable compiler")


    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version])
        os.rename("{}-{}".format(self.name, self.version), self._source_subfolder)

    def package(self):
        self.copy(pattern="LICENSE", src=self._source_subfolder, dst="licenses")
        self.copy(pattern="*.h", src=os.path.join(self._source_subfolder, "include"), dst="include")
        self.copy(pattern="*.hpp", src=os.path.join(self._source_subfolder, "include"), dst="include")

    def package_id(self):
        self.info.header_only()
