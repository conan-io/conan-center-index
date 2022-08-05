import os
from conan import ConanFile, tools
from conans.errors import ConanInvalidConfiguration


class TupletConan(ConanFile):
    name = "tuplet"
    license = "BSL-1.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/codeinred/tuplet"
    description = "A fast, simple tuple implementation that implements tuple as an aggregate"
    topics = ("tuple", "trivially-copyable", "modern-c++")
    settings = ("compiler", "arch", "os", "build_type")
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _min_cppstd(self):
        return "20"

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "9",
            "Visual Studio": "16.2",
            "msvc": "19.22",
            "clang": "10",
            "apple-clang": "11"
        }

    def source(self):
        tools.files.get(self,
            **self.conan_data["sources"][self.version],
            strip_root=True,
            destination=self._source_subfolder
        )

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, self._min_cppstd)

        def lazy_lt_semver(v1, v2):
            lv1 = [int(v) for v in v1.split(".")]
            lv2 = [int(v) for v in v2.split(".")]
            min_length = min(len(lv1), len(lv2))
            return lv1[:min_length] < lv2[:min_length]

        compiler = str(self.settings.compiler)
        version = str(self.settings.compiler.version)

        minimum_version = self._compilers_minimum_version.get(compiler, False)

        if not minimum_version:
            self.output.warn(
                f"{self.name} requires C++20. Your compiler ({compiler}) is unknown. Assuming it supports C++20.")
        elif lazy_lt_semver(version, minimum_version):
            raise ConanInvalidConfiguration(
                f"{self.name} {self.version} requires C++20, which your compiler ({compiler}-{version}) does not support")

    def package_id(self):
        self.info.header_only()

    def package(self):
        include_folder = os.path.join(self._source_subfolder, "include")
        self.copy(pattern="*.hpp", dst="include", src=include_folder)
        self.copy(pattern="LICENSE", dst="licenses",
                  src=self._source_subfolder)
