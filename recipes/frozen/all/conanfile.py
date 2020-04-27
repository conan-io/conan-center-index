from conans import ConanFile, CMake, tools
import os.path


class FrozenConan(ConanFile):
    name = "frozen"
    description = "A header-only, constexpr alternative to gperf for C++14 users."
    homepage = "https://github.com/serge-sans-paille/frozen"
    url = "https://github.com/conan-io/conan-center-index"
    license = "Apache-2.0"
    topics = ("gperf")
    exports_sources = ["CMakeLists.txt"]
    settings = "compiler"
    generators = "cmake"
    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def package(self):
        self.copy(pattern="*.h", dst="include", src=os.path.join(self._source_subfolder, "include"))
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)

    def package_id(self):
        self.info.header_only()
