import os
from conans import ConanFile, tools
from conan.errors import ConanInvalidConfiguration

required_conan_version = ">=1.33.0"

class LupleConan(ConanFile):
    name = "luple"
    license = "Unlicense"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/alexpolt/luple"
    description = "Home to luple, nuple, C++ String Interning, Struct Reader and C++ Type Loophole"
    topics = ("conan", "loophole", "luple", "nuple", "struct", "intern")
    settings = "compiler"
    no_copy_source = True

    def validate(self):
        minimal_cpp_standard = "14"
        if self.settings.compiler.cppstd:
            tools.build.check_min_cppstd(self, minimal_cpp_standard)
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
        version = tools.scm.Version(self.settings.compiler.version)
        if version < minimal_version[compiler]:
            raise ConanInvalidConfiguration("%s requires a compiler that supports at least C++%s" % (self.name, minimal_cpp_standard))

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version][0], strip_root=True)
        tools.files.download(self, filename="LICENSE", **self.conan_data["sources"][self.version][1])

    def package(self):
        self.copy("LICENSE", dst="licenses")
        self.copy("*.h", dst="include")

    def package_id(self):
        self.info.header_only()

    def package_info(self):
        self.cpp_info.libdirs = []
