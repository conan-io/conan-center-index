from conans import ConanFile, tools, CMake
import os

required_conan_version = ">=1.28.0"

class CrowConan(ConanFile):
    name = "crow"
    homepage = "https://github.com/ipkn/crow"
    description = "Crow is C++ microframework for web. (inspired by Python Flask)"
    topics = ("conan", "web", "microframework", "header-only")
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "compiler", "arch", "build_type"
    generators = "cmake", "cmake_find_package", "cmake_find_package_multi"
    exports_sources = ["patches/*"]
    license = "BSD3"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def requirements(self):
        self.requires("openssl/1.1.1h")
        self.requires("boost/1.69.0")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = "crow-" + self.version
        os.rename(extracted_dir, self._source_subfolder)
        tools.patch(**self.conan_data["patches"][self.version])

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.configure(source_folder=self._source_subfolder)
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE*", dst="licenses", src=self._source_subfolder)
        self.copy("*.h", dst="include/crow", src="amalgamate")

    def package_id(self):
        self.info.header_only()
