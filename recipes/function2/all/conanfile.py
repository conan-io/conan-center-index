import os

from conans import ConanFile, tools
from conan.errors import ConanInvalidConfiguration


class Function2Conan(ConanFile):
    name = "function2"
    description = "Improved and configurable drop-in replacement to std::function that supports move only types, multiple overloads and more"
    topics = ("function", "functional", "function-wrapper", "type-erasure", "header-only")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/Naios/function2"
    license = "BSL-1.0"
    settings = "compiler"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def configure(self):
        minimal_cpp_standard = "14"
        if self.settings.compiler.cppstd:
            tools.build.check_min_cppstd(self, self, minimal_cpp_standard)
        minimal_version = {
            "gcc": "5",
            "clang": "3.4",
            "apple-clang": "10",
            "Visual Studio": "14"
        }
        compiler = str(self.settings.compiler)
        if compiler not in minimal_version:
            self.output.warn(
                "%s recipe lacks information about the %s compiler standard version support" % (self.name, compiler))
            self.output.warn(
                "%s requires a compiler that supports at least C++%s" % (self.name, minimal_cpp_standard))
            return
        version = tools.Version(self.settings.compiler.version)
        if version < minimal_version[compiler]:
            raise ConanInvalidConfiguration("%s requires a compiler that supports at least C++%s" % (self.name, minimal_cpp_standard))

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version])
        extracted_dir = "function2-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def package(self):
        self.copy(pattern="LICENSE.txt", dst="licenses", src=self._source_subfolder)
        self.copy(pattern="*.hpp", dst=os.path.join("include", "function2"), src=os.path.join(self._source_subfolder, "include", "function2"))

    def package_id(self):
        self.info.header_only()
