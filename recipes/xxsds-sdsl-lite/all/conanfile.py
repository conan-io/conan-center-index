import os
from conans import ConanFile, tools

required_conan_version = ">=1.33.0"

class XXSDSSDSLLite(ConanFile):
    name = "xxsds-sdsl-lite"
    description = "SDSL - Succinct Data Structure Library"
    homepage = "https://github.com/xxsds/sdsl-lite"
    url = "https://github.com/conan-io/conan-center-index"
    license = "BSD-3-Clause"
    topics = ("conan", "sdsl", "succint", "data-structures")
    settings = "compiler"
    exports_sources = "patches/*"
    provides = "sdsl-lite"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, 11)

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.patch(self, **patch)

    def package(self):
        self.copy("*.hpp", dst="include",
                  src=os.path.join(self._source_subfolder, "include"))
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)

    def package_id(self):
        self.info.header_only()

    def package_info(self):
        if self.settings.compiler == "Visual Studio":
            self.cpp_info.defines.append("MSVC_COMPILER")
        self.cpp_info.names["pkgconfig"] = "sdsl-lite"
        self.cpp_info.names["cmake_find_package"] = "sdsl-lite"
        self.cpp_info.names["cmake_find_package_multi"] = "sdsl-lite"
