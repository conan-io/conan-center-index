from conans import ConanFile, tools
from conan.errors import ConanInvalidConfiguration
import os


class CistaConan(ConanFile):
    name = "cista"
    description = (
        "Cista++ is a simple, open source (MIT license) C++17 "
        "compatible way of (de-)serializing C++ data structures."
    )
    license = "MIT"
    topics = ("cista", "serialization", "deserialization", "reflection")
    homepage = "https://github.com/felixguendling/cista"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "compiler"
    no_copy_source = True

    @property
    def _compilers_minimum_version(self):
        return {
            "Visual Studio": "15.7",
            "gcc": "8",
            "clang": "6",
            "apple-clang": "9.1"
        }

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.build.check_min_cppstd(self, 17)

        def lazy_lt_semver(v1, v2):
            lv1 = [int(v) for v in v1.split(".")]
            lv2 = [int(v) for v in v2.split(".")]
            min_length = min(len(lv1), len(lv2))
            return lv1[:min_length] < lv2[:min_length]

        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), None)
        if minimum_version and lazy_lt_semver(str(self.settings.compiler.version), minimum_version):
            raise ConanInvalidConfiguration(
                "{} {} requires C++17, which your compiler does not support.".format(self.name, self.version)
            )

    def package_id(self):
        self.info.header_only()

    def source(self):
        for file in self.conan_data["sources"][self.version]:
            filename = os.path.basename(file["url"])
            tools.files.download(self, filename=filename, **file)

    def package(self):
        self.copy("LICENSE", dst="licenses")
        self.copy("cista.h", dst="include")

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "cista"
        self.cpp_info.names["cmake_find_package_multi"] = "cista"
