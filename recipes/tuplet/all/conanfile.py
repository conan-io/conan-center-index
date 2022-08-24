import os
from conan import ConanFile, tools
from conan.errors import ConanInvalidConfiguration


class TupletConan(ConanFile):
    name = "tuplet"
    license = "BSL-1.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/codeinred/tuplet"
    description = "A fast, simple tuple implementation that implements tuple as an aggregate"
    topics = ("tuple", "trivially-copyable", "modern-cpp")
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
            "gcc": "11",
            "Visual Studio": "17",
            "msvc": "19.22",
            "clang": "13",
            "apple-clang": "13"
        }

    def source(self):
        tools.files.get(self,
                        **self.conan_data["sources"][self.version],
                        strip_root=True,
                        destination=self._source_subfolder
                        )

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.build.check_min_cppstd(self, self._min_cppstd)

        def lazy_lt_semver(v1, v2):
            lv1 = [int(v) for v in v1.split(".")]
            lv2 = [int(v) for v in v2.split(".")]
            min_length = min(len(lv1), len(lv2))
            return lv1[:min_length] < lv2[:min_length]

        compiler = str(self.settings.compiler)
        version = str(self.settings.compiler.version)

        minimum_version = self._compilers_minimum_version.get(compiler, False)

        if not minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.name} requires C++20. Your compiler configuration ({compiler}-{version}) wasn't validated. \
                please report an issue if it does actually supports c++20.")
        elif lazy_lt_semver(version, minimum_version):
            raise ConanInvalidConfiguration(
                f"{self.name} {self.version} requires C++20, which your compiler ({compiler}-{version}) does not support")

    def build(self):
        pass

    def package_id(self):
        self.info.header_only()

    def package(self):
        source_folder = os.path.join(
            self.source_folder, self._source_subfolder)
        include_folder = os.path.join(
            self.source_folder, self._source_subfolder, "include")

        tools.files.copy(self, pattern="*.hpp",
                         dst=os.path.join(self.package_folder, "include"),
                         src=include_folder)
        tools.files.copy(self, pattern="LICENSE",
                         dst=os.path.join(self.package_folder, "licenses"),
                         src=source_folder)
