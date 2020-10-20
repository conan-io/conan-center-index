from conans import ConanFile, tools
import os


class LibmortonConan(ConanFile):
    name = "libmorton"
    description = "C++ header-only library with methods to efficiently " \
                  "encode/decode 64, 32 and 16-bit Morton codes and coordinates, in 2D and 3D."
    license = "MIT"
    topics = ("conan", "libmorton", "morton", "encoding", "decoding")
    homepage = "https://github.com/Forceflow/libmorton"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "compiler"
    exports_sources = "patches/**"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def package_id(self):
        self.info.header_only()

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename(self.name + "-" + self.version, self._source_subfolder)

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy("*.h", dst="include", src=os.path.join(self._source_subfolder, "libmorton", "include"))

    def package_info(self):
        if self.settings.compiler == "Visual Studio":
            self.cpp_info.defines = ["NOMINMAX"]
        if self.settings.os == "Linux":
            self.cpp_info.system_libs = ["m"]
