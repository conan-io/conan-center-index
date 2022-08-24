from conans import ConanFile, tools
import os

required_conan_version = ">=1.33.0"


class MioConan(ConanFile):
    name = "mio"
    description = "Cross-platform C++11 header-only library for memory mapped file IO."
    license = "MIT"
    topics = ("mio", "mmap", "memory-mapping", "fileviewer")
    homepage = "https://github.com/mandreyel/mio"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "compiler"
    exports_sources = "patches/**"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, 11)

    def package_id(self):
        self.info.header_only()

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.patch(self, **patch)

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy("*pp", dst="include", src=os.path.join(self._source_subfolder, "include"))

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "mio"
        self.cpp_info.names["cmake_find_package_multi"] = "mio"

        self.cpp_info.components["mio-headers"].names["cmake_find_package"] = "mio-headers"
        self.cpp_info.components["mio-headers"].names["cmake_find_package_multi"] = "mio-headers"

        if self.settings.os == "Windows":
            self.cpp_info.components["mio_full_winapi"].names["cmake_find_package"] = "mio_full_winapi"
            self.cpp_info.components["mio_full_winapi"].names["cmake_find_package_multi"] = "mio_full_winapi"

            self.cpp_info.components["mio_min_winapi"].names["cmake_find_package"] = "mio_min_winapi"
            self.cpp_info.components["mio_min_winapi"].names["cmake_find_package_multi"] = "mio_min_winapi"
            self.cpp_info.components["mio_min_winapi"].defines = ["WIN32_LEAN_AND_MEAN", "NOMINMAX"]
