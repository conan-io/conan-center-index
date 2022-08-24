from conans import ConanFile, tools
from conan.errors import ConanInvalidConfiguration
import os


class EarcutConan(ConanFile):
    name = "earcut"
    description = "A C++ port of earcut.js, a fast, header-only polygon triangulation library."
    homepage = "https://github.com/mapbox/earcut.hpp"
    url = "https://github.com/conan-io/conan-center-index"
    license = "ISC"
    topics = ("algorithm", "cpp", "geometry", "rendering", "triangulation",
              "polygon", "header-only", "tessellation", "earcut")
    settings = "compiler"
    no_copy_source = True

    @property
    def _minimum_compilers_version(self):
        # References:
        # * https://github.com/mapbox/earcut.hpp#dependencies
        # * https://en.cppreference.com/w/cpp/compiler_support/11
        # * https://en.wikipedia.org/wiki/Xcode#Toolchain_versions
        return {
            "apple-clang": "5.1",
            "clang": "3.4",
            "gcc": "4.9",
            "intel": "15",
            "sun-cc": "5.14",
            "Visual Studio": "12"
        }

    @property
    def _minimum_cpp_standard(self):
        return 11

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.build.check_min_cppstd(self, self._minimum_cpp_standard)

        def lazy_lt_semver(v1, v2):
            lv1 = [int(v) for v in v1.split(".")]
            lv2 = [int(v) for v in v2.split(".")]
            min_length = min(len(lv1), len(lv2))
            return lv1[:min_length] < lv2[:min_length]

        min_version = self._minimum_compilers_version.get(
            str(self.settings.compiler))
        if not min_version:
            self.output.warn("{} recipe lacks information about the {} compiler support.".format(
                self.name, self.settings.compiler))
        else:
            if lazy_lt_semver(str(self.settings.compiler.version), min_version):
                raise ConanInvalidConfiguration("{} requires C++{} support. The current compiler {} {} does not support it.".format(
                    self.name, self._minimum_cpp_standard, self.settings.compiler, self.settings.compiler.version))

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def package(self):
        self.copy("*", "include",
                  src=os.path.join(self._source_subfolder, "include"))
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)

    def package_id(self):
        self.info.header_only()
