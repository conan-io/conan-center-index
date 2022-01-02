import os
from conans import ConanFile, tools
from conans.errors import ConanInvalidConfiguration

required_conan_version = ">=1.33.0"

class VequeConan(ConanFile):
    name = "veque"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/Shmoopty/veque"
    description = "Fast C++ container combining the best features of std::vector and std::deque"
    topics = ("cpp17", "vector", "deque")
    license = "BSL-1.0"

    settings = "os", "arch", "compiler", "build_type"
    exports_sources = ["patches/**",]
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "7",
            "clang": "5",
            "apple-clang": "10",
            "Visual Studio": "15.7",
        }

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, "17")

        def lazy_lt_semver(v1, v2):
            lv1 = [int(v) for v in v1.split(".")]
            lv2 = [int(v) for v in v2.split(".")]
            min_length = min(len(lv1), len(lv2))
            return lv1[:min_length] < lv2[:min_length]

        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and lazy_lt_semver(str(self.settings.compiler.version), minimum_version):
            raise ConanInvalidConfiguration("{} requires C++17, which your compiler does not support.".format(self.name))

    def package_id(self):
        self.info.header_only()

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)
        self._patch_sources()

    def package(self):
        self.copy("*.hpp", dst="include", src=os.path.join(self._source_subfolder, "include"))
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
