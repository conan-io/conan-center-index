from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os
import shutil


class VariantConan(ConanFile):
    name = "mpark_variant"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/mpark/variant"
    description = "C++17 std::variant for C++11/14/17"
    license = "BSL-1.0"
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake"

    settings = "os", "arch", "compiler", "build_type"

    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"
    _cmake = None

    def configure(self):
        if self.settings.compiler == "Visual Studio" and int(self.settings.compiler.version.value) <= 12:
            raise ConanInvalidConfiguration("Required MSVC 2015 Update 3 or superior")  # https://github.com/mpark/variant/blob/v1.3.0/include/mpark/config.hpp#L11

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = "variant-" + self.version

        # Work to remove 'deps' directory, just to be sure.
        shutil.rmtree(os.path.join(extracted_dir, "3rdparty"))

        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        if not self._cmake:
            self._cmake = CMake(self)
            self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        self.copy(pattern="LICENSE.md", dst="licenses", src=self._source_subfolder)
        tools.rmdir(os.path.join(self.package_folder, "lib"))
    
    def package_id(self):
        self.info.header_only()
    
    def package_info(self):
        pass
