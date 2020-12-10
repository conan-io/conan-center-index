from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os


class TlConan(ConanFile):
    name = "tl"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://tl.tartanllama.xyz"
    description = "tl is a collection of generic C++ libraries"
    topics = ("conan", "c++", "utilities")
    settings = "compiler"
    license = "CC0-1.0"
    no_copy_source = True
    _source_subfolder = "tl"

    def configure(self):
        minimal_cpp_standard = "14"
        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, minimal_cpp_standard)

        minimal_version = {
            "gcc": "6.4",
            "clang": "5",
            "apple-clang": "10",
            "Visual Studio": "15"
        }

        def lt_compiler_version(version1, version2):
            v1, *v1_res = version1.split(".", 1)
            v2, *v2_res = version2.split(".", 1)
            if v1 == v2 and v1_res and v2_res:
                return lt_compiler_version(v1_res, v2_res)
            return v1 < v2

        compiler = str(self.settings.compiler)
        if compiler not in minimal_version:
            self.output.warn(
                "{} recipe lacks information about the {} compiler standard version support".format(self.name, compiler))
            self.output.warn(
                "{} requires a compiler that supports at least C++{}".format(self.name, minimal_cpp_standard))
        elif lt_compiler_version(str(self.settings.compiler.version), minimal_version[compiler]):
            raise ConanInvalidConfiguration(
                "{} requires a compiler that supports at least C++{}".format(self.name, minimal_cpp_standard))

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("tl-%s" % self.version, self._source_subfolder)

    def package(self):
        self.copy("*.hpp",
                  src=os.path.join(self._source_subfolder, "include"),
                  dst="include")
        self.copy("COPYING", src=self._source_subfolder, dst="licenses")

    def package_id(self):
        self.info.header_only()
