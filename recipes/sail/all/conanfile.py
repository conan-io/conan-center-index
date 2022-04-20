from conans.errors import ConanInvalidConfiguration
from conan.tools.files import rename
from conans import ConanFile, CMake, tools
import os

required_conan_version = ">=1.43.0"

class SAILConan(ConanFile):
    name = "sail"
    version = "0.9.0"
    description = "The missing small and fast image decoding library for humans (not for machines)"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://sail.software"
    topics = ( "image", "encoding", "decoding", "graphics" )
    license = "MIT"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }
    generators = "cmake", "cmake_find_package", "cmake_find_package_multi"
    exports_sources = "CMakeLists.txt"

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        self.requires("giflib/5.2.1")
        self.requires("libavif/0.9.3")
        self.requires("libjpeg/9d")
        self.requires("libpng/1.6.37")
        self.requires("libtiff/4.3.0")
        self.requires("libwebp/1.2.2")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, "17")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  strip_root=True, destination=self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake

        self._cmake = CMake(self)
        self._cmake.definitions["SAIL_BUILD_APPS"]     = "OFF"
        self._cmake.definitions["SAIL_BUILD_EXAMPLES"] = "OFF"
        self._cmake.definitions["SAIL_BUILD_TESTS"]    = "OFF"
        self._cmake.definitions["SAIL_COMBINE_CODECS"] = "ON"
        self._cmake.configure(build_folder=self._build_subfolder)

        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE.txt",       src=self._source_subfolder, dst="licenses")
        self.copy("LICENSE.INIH.txt",  src=self._source_subfolder, dst="licenses")
        self.copy("LICENSE.MUNIT.txt", src=self._source_subfolder, dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()
        # Remove CMake and pkg-config rules
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        # Move icons
        rename(self, os.path.join(self.package_folder, "share"),
                     os.path.join(self.package_folder, "res"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "Sail")

        self.cpp_info.filenames["cmake_find_package"]       = "Sail"
        self.cpp_info.filenames["cmake_find_package_multi"] = "Sail"
        self.cpp_info.names["cmake_find_package"]           = "SAIL"
        self.cpp_info.names["cmake_find_package_multi"]     = "SAIL"

        self.cpp_info.components["sail-common"].set_property("cmake_target_name", "SAIL::SailCommon")
        self.cpp_info.components["sail-common"].set_property("pkg_config_name", "libsail-common")
        self.cpp_info.components["sail-common"].names["cmake_find_package"]       = "SailCommon"
        self.cpp_info.components["sail-common"].names["cmake_find_package_multi"] = "SailCommon"
        self.cpp_info.components["sail-common"].libs = ["sail-common"]

        self.cpp_info.components["sail-codecs"].set_property("cmake_target_name", "SAIL::SailCodecs")
        self.cpp_info.components["sail-codecs"].names["cmake_find_package"]       = "SailCodecs"
        self.cpp_info.components["sail-codecs"].names["cmake_find_package_multi"] = "SailCodecs"
        self.cpp_info.components["sail-codecs"].libs = ["sail-codecs"]
        self.cpp_info.components["sail-codecs"].requires = ["sail-common", "avif", "GIF::GIF", "JPEG::JPEG",
                                                            "PNG::PNG", "TIFF::TIFF", "WebP::webpdecoder", "WebP::webpdemux"]

        self.cpp_info.components["libsail"].set_property("cmake_target_name", "SAIL::Sail")
        self.cpp_info.components["libsail"].set_property("pkg_config_name", "libsail")
        self.cpp_info.components["libsail"].names["cmake_find_package"] = "Sail"
        self.cpp_info.components["libsail"].names["cmake_find_package_multi"] = "Sail"
        self.cpp_info.components["libsail"].libs = ["sail"]
        self.cpp_info.components["libsail"].requires = ["sail-common", "sail-codecs"]

        self.cpp_info.components["sail-manip"].set_property("cmake_target_name", "SAIL::SailManip")
        self.cpp_info.components["sail-manip"].set_property("pkg_config_name", "libsail-manip")
        self.cpp_info.components["sail-manip"].names["cmake_find_package"]       = "SailManip"
        self.cpp_info.components["sail-manip"].names["cmake_find_package_multi"] = "SailManip"
        self.cpp_info.components["sail-manip"].libs = ["sail-manip"]
        self.cpp_info.components["sail-manip"].requires = ["sail-common"]

        self.cpp_info.components["sail-c++"].set_property("cmake_target_name", "SAIL::SailC++")
        self.cpp_info.components["sail-c++"].set_property("pkg_config_name", "libsail-c++")
        self.cpp_info.components["sail-c++"].names["cmake_find_package"]       = "SailC++"
        self.cpp_info.components["sail-c++"].names["cmake_find_package_multi"] = "SailC++"
        self.cpp_info.components["sail-c++"].libs = ["sail-c++"]
        self.cpp_info.components["sail-c++"].requires = ["libsail", "sail-manip"]
