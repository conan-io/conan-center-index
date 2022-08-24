from conan import ConanFile, tools
import os

required_conan_version = ">=1.33.0"


class PcgcppConan(ConanFile):
    name = "pcg-cpp"
    description = "C++ implementation of the PCG family of random number generators."
    license = ("MIT", "Apache-2.0")
    topics = ("pcg-cpp", "pcg", "rng", "random")
    homepage = "https://github.com/imneme/pcg-cpp"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "compiler"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.build.check_min_cppstd(self, 11)

    def package_id(self):
        self.info.header_only()

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def package(self):
        self.copy("LICENSE*", dst="licenses", src=self._source_subfolder)
        self.copy("*", dst="include", src=os.path.join(self._source_subfolder, "include"))
