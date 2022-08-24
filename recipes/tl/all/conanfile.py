from conans import ConanFile, tools
from conan.errors import ConanInvalidConfiguration
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

    @property
    def _source_subfolder(self):
        return "source_subfolder"

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

        def lazy_lt_semver(v1, v2):
            lv1 = [int(v) for v in v1.split(".")]
            lv2 = [int(v) for v in v2.split(".")]
            min_length = min(len(lv1), len(lv2))
            return lv1[:min_length] < lv2[:min_length]

        compiler = str(self.settings.compiler)
        if compiler not in minimal_version:
            self.output.warn(
                "{} recipe lacks information about the {} compiler standard version support".format(self.name, compiler))
            self.output.warn(
                "{} requires a compiler that supports at least C++{}".format(self.name, minimal_cpp_standard))
        elif lazy_lt_semver(str(self.settings.compiler.version), minimal_version[compiler]):
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
