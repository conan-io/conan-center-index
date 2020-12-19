import os
from conans import ConanFile, CMake, tools


class LibFtdiConan(ConanFile):
    name = "libftdi"
    description = "A library to talk to FTDI chips"
    license = ["GNU LGPL v2.1"]
    topics = ("conan", "libftdi1")
    homepage = "https://www.intra2net.com/en/developer/libftdi/"
    url = "https://github.com/conan-io/conan-center-index"
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake", "cmake_find_package", "pkg_config"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    requires = (
            "libusb/1.0.23",
            "boost/1.74.0"
            )
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = "libftdi1-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _patch_cmakelists(self, subfolder):
        cmakelists_path = os.path.join(self._source_subfolder, subfolder, "CMakeLists.txt")
        tools.replace_in_file(cmakelists_path, "CMAKE_SOURCE_DIR", "PROJECT_SOURCE_DIR", strict=False)
        tools.replace_in_file(cmakelists_path, "CMAKE_BINARY_DIR", "PROJECT_BINARY_DIR", strict=False)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake

        self._cmake = CMake(self)
        options = {
            "BUILD_TESTS": False,
            "EXAMPLES": False,
            "FTDI_EEPROM": False,
            "FTDIPP" : True,
            "STATICLIBS": not self.options.shared
        }
        self._cmake.definitions.update(options)
        self._cmake.configure()
        return self._cmake

    def build(self):
        self._patch_cmakelists("")
        self._patch_cmakelists("ftdipp")
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        os.unlink(os.path.join(self.package_folder, "bin", "libftdi1-config"))

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "LibFTDI1"
        self.cpp_info.names["cmake_find_package_multi"] = "LibFTDI1"
        self.cpp_info.names["pkgconfig"] = "libftdi1"
        self.cpp_info.includedirs.append(
            os.path.join(self.package_folder, "include", "libftdi1")
        )
        self.cpp_info.libs = ["ftdipp1", "ftdi1"]
