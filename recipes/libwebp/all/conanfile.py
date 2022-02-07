from conans import ConanFile, CMake, tools
import os

required_conan_version = ">=1.43.0"


class LibwebpConan(ConanFile):
    name = "libwebp"
    description = "Library to encode and decode images in WebP format"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/webmproject/libwebp"
    topics = ("image", "libwebp", "webp", "decoding", "encoding")
    license = "BSD-3-Clause"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_simd": [True, False],
        "near_lossless": [True, False],
        "swap_16bit_csp": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_simd": True,
        "near_lossless": True,
        "swap_16bit_csp": False,
    }

    generators = "cmake"
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def export_sources(self):
        self.copy("CMakeLists.txt")
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    @property
    def _version_components(self):
        return [int(x) for x in self.version.split(".")]

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        # should be an option but it doesn't work yet
        self._cmake.definitions["WEBP_ENABLE_SIMD"] = self.options.with_simd
        if self._version_components[0] >= 1:
            self._cmake.definitions["WEBP_NEAR_LOSSLESS"] = self.options.near_lossless
        else:
            self._cmake.definitions["WEBP_ENABLE_NEAR_LOSSLESS"] = self.options.near_lossless
        self._cmake.definitions["WEBP_ENABLE_SWAP_16BIT_CSP"] = self.options.swap_16bit_csp
        # avoid finding system libs
        self._cmake.definitions["CMAKE_DISABLE_FIND_PACKAGE_GIF"] = True
        self._cmake.definitions["CMAKE_DISABLE_FIND_PACKAGE_PNG"] = True
        self._cmake.definitions["CMAKE_DISABLE_FIND_PACKAGE_TIFF"] = True
        self._cmake.definitions["CMAKE_DISABLE_FIND_PACKAGE_JPEG"] = True
        self._cmake.definitions["WEBP_BUILD_ANIM_UTILS"] = False
        self._cmake.definitions["WEBP_BUILD_CWEBP"] = False
        self._cmake.definitions["WEBP_BUILD_DWEBP"] = False
        self._cmake.definitions["WEBP_BUILD_IMG2WEBP"] = False
        self._cmake.definitions["WEBP_BUILD_GIF2WEBP"] = False
        self._cmake.definitions["WEBP_BUILD_VWEBP"] = False
        self._cmake.definitions["WEBP_BUILD_EXTRAS"] = False
        self._cmake.definitions["WEBP_BUILD_WEBPINFO"] = False
        if tools.Version(self.version) >= "1.2.1":
            self._cmake.definitions["WEBP_BUILD_LIBWEBPMUX"] = True
        self._cmake.definitions["WEBP_BUILD_WEBPMUX"] = False

        self._cmake.configure()

        return self._cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        self.copy("COPYING", dst="licenses", src=self._source_subfolder)
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "WebP")
        self.cpp_info.set_property("pkg_config_name", "libwebp-all-do-not-use")

        # webpdecoder
        self.cpp_info.components["webpdecoder"].set_property("cmake_target_name", "WebP::webpdecoder")
        self.cpp_info.components["webpdecoder"].set_property("pkg_config_name", "libwebpdecoder")
        self.cpp_info.components["webpdecoder"].libs = ["webpdecoder"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["webpdecoder"].system_libs = ["pthread"]

        # webp
        self.cpp_info.components["webp"].set_property("cmake_target_name", "WebP::webp")
        self.cpp_info.components["webp"].set_property("pkg_config_name", "libwebp")
        self.cpp_info.components["webp"].libs = ["webp"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["webp"].system_libs = ["m", "pthread"]

        # webpdemux
        self.cpp_info.components["webpdemux"].set_property("cmake_target_name", "WebP::webpdemux")
        self.cpp_info.components["webpdemux"].set_property("pkg_config_name", "libwebpdemux")
        self.cpp_info.components["webpdemux"].libs = ["webpdemux"]
        self.cpp_info.components["webpdemux"].requires = ["webp"]

        # webpmux
        self.cpp_info.components["webpmux"].set_property("cmake_target_name", "WebP::libwebpmux")
        self.cpp_info.components["webpmux"].set_property("pkg_config_name", "libwebpmux")
        self.cpp_info.components["webpmux"].libs = ["webpmux"]
        self.cpp_info.components["webpmux"].requires = ["webp"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["webpmux"].system_libs = ["m"]

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.names["cmake_find_package"] = "WebP"
        self.cpp_info.names["cmake_find_package_multi"] = "WebP"
        self.cpp_info.names["pkg_config"] = "libwebp-all-do-not-use"
        self.cpp_info.components["webpmux"].names["cmake_find_package"] = "libwebpmux"
        self.cpp_info.components["webpmux"].names["cmake_find_package_multi"] = "libwebpmux"
