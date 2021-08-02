import os
from conans import ConanFile, CMake, tools

required_conan_version = ">=1.33.0"


class Exiv2Conan(ConanFile):
    name = "exiv2"
    description = "Exiv2 is a C++ library and a command-line utility " \
                  "to read, write, delete and modify Exif, IPTC, XMP and ICC image metadata."
    license = "GPL-2.0"
    topics = ("conan", "image", "exif", "xmp")
    homepage = "https://www.exiv2.org"
    url = "https://github.com/conan-io/conan-center-index"
    exports_sources = ["CMakeLists.txt", "patches/**"]
    generators = "cmake", "cmake_find_package"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_png": [True, False],
        "with_xmp": [False, "bundled", "external"],
        "with_curl": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_png": True,
        "with_xmp": "bundled",
        "with_curl": False,
    }

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
        self.requires("libiconv/1.16")
        if self.options.with_png:
            self.requires("libpng/1.6.37")
        if self.options.with_xmp == "bundled":
            self.requires("expat/2.4.1")
        if self.options.with_curl:
            self.requires("libcurl/7.64.1")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["EXIV2_BUILD_SAMPLES"] = False
        self._cmake.definitions["EXIV2_BUILD_EXIV2_COMMAND"] = False
        self._cmake.definitions["EXIV2_ENABLE_PNG"] = self.options.with_png
        self._cmake.definitions["EXIV2_ENABLE_XMP"] = self.options.with_xmp == "bundled"
        self._cmake.definitions["EXIV2_ENABLE_EXTERNAL_XMP"] = self.options.with_xmp == "external"
        self._cmake.definitions["EXIV2_ENABLE_NLS"] = False
        self._cmake.definitions["EXIV2_ENABLE_WEBREADY"] = self.options.with_curl
        self._cmake.definitions["EXIV2_ENABLE_CURL"] = self.options.with_curl
        self._cmake.definitions["EXIV2_ENABLE_SSH"] = False
        self._cmake.definitions["EXIV2_ENABLE_DYNAMIC_RUNTIME"] = (self.settings.compiler == "Visual Studio" and
                "MD" in self.settings.compiler.runtime)
        # set PIC manually because of object target exiv2_int
        self._cmake.definitions["CMAKE_POSITION_INDEPENDENT_CODE"] = self.options.get_safe("fPIC", True)
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def package(self):
        self.copy("COPYING", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "exiv2"
        self.cpp_info.names["cmake_find_package_multi"] = "exiv2"
        self.cpp_info.names["pkgconfig"] = "exiv2"

        # component exiv2lib
        self.cpp_info.components["exiv2lib"].libs = ["exiv2"]
        self.cpp_info.components["exiv2lib"].requires = [ "libiconv::libiconv"]
        if self.options.with_png:
            self.cpp_info.components["exiv2lib"].requires.append("libpng::libpng")
        if self.options.with_curl:
            self.cpp_info.components["exiv2lib"].requires.append("libcurl::libcurl")

        if self.settings.os in ("FreeBSD", "Linux"):
            self.cpp_info.components["exiv2lib"].system_libs.extend(["pthread"])
        if self.settings.os == "Windows":
            self.cpp_info.components["exiv2lib"].system_libs.extend(["psapi", "ws2_32"])
            self.cpp_info.components["exiv2lib"].defines.append("WIN32_LEAN_AND_MEAN")

        # component exiv2-xmp
        if self.options.with_xmp == "bundled":
            self.cpp_info.components["exiv2-xmp"].libs = ["exiv2-xmp"]
            self.cpp_info.components["exiv2-xmp"].requires = [ "expat::expat" ]
