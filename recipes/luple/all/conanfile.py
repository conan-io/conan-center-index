import os
from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration

required_conan_version = ">=1.32.0"

class LupleConan(ConanFile):
    name = "luple"
    license = "Unlicense"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/alexpolt/luple"
    description = "Home to luple, nuple, C++ String Interning, Struct Reader and C++ Type Loophole"
    topics = ("conan", "loophole", "luple", "nuple", "struct", "intern")
    settings = "compiler"

    def configure(self):
        minimal_cpp_standard = "14"
        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, minimal_cpp_standard)
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

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def package(self):
        tools.save(os.path.join(self.package_folder, "licenses", "COPYING"), "Public Domain")
        self.copy("*.h", dst="include", src=self._source_subfolder)

    def package_id(self):
        self.info.header_only()

    def package_info(self):
        self.cpp_info.libdirs = []
