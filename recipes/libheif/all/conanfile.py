from conan import ConanFile, tools
from conans import CMake
import os

required_conan_version = ">=1.43.0"


class Libheif(ConanFile):
    name = "libheif"
    description = "libheif is an HEIF and AVIF file format decoder and encoder."
    topics = ("libheif", "heif", "codec", "video")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/strukturag/libheif"
    license = ("LGPL-3.0-only", "GPL-3.0-or-later", "MIT")

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_x265": [True, False],
        "with_dav1d": [True, False],
        "with_libaomav1": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_x265": False,
        "with_dav1d": False,
        "with_libaomav1": False,
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
        if tools.Version(self.version) < "1.11.0":
            # dav1d supported since 1.10.0 but usable option `WITH_DAV1D`
            # for controlling support exists only since 1.11.0
            del self.options.with_dav1d

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        self.requires("libde265/1.0.8")
        if self.options.with_x265:
            self.requires("libx265/3.4")
        if self.options.with_libaomav1:
            self.requires("libaom-av1/3.1.2")
        if self.options.get_safe("with_dav1d"):
            self.requires("dav1d/0.9.1")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, 11)

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.patch(self, **patch)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["WITH_EXAMPLES"] = False
        self._cmake.definitions["WITH_RAV1E"] = False
        # x265
        self._cmake.definitions["CMAKE_DISABLE_FIND_PACKAGE_X265"] = not self.options.with_x265
        self._cmake.definitions["WITH_X265"] = self.options.with_x265
        # aom
        self._cmake.definitions["CMAKE_DISABLE_FIND_PACKAGE_LibAOM"] = not self.options.with_libaomav1
        self._cmake.definitions["WITH_AOM"] = self.options.with_libaomav1
        # dav1d
        self._cmake.definitions["WITH_DAV1D"] = self.options.get_safe("with_dav1d", False)

        # Workaround for cross-build to at least iOS/tvOS/watchOS,
        # when dependencies are found with find_path() and find_library()
        # TODO: won't be necessary with CMakeToolchain (https://github.com/conan-io/conan/pull/10186)
        if tools.build.cross_building(self, self):
            self._cmake.definitions["CMAKE_FIND_ROOT_PATH_MODE_INCLUDE"] = "BOTH"
            self._cmake.definitions["CMAKE_FIND_ROOT_PATH_MODE_LIBRARY"] = "BOTH"

        self._cmake.configure()
        return self._cmake

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("COPYING", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "libheif")
        self.cpp_info.set_property("cmake_target_name", "libheif::heif")
        self.cpp_info.set_property("pkg_config_name", "libheif")
        # TODO: back to global scope in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.components["heif"].libs = ["heif"]
        if not self.options.shared:
            self.cpp_info.components["heif"].defines = ["LIBHEIF_STATIC_BUILD"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["heif"].system_libs.extend(["m", "pthread"])
        if not self.options.shared and tools.stdcpp_library(self):
            self.cpp_info.components["heif"].system_libs.append(tools.stdcpp_library(self))

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.components["heif"].set_property("cmake_target_name", "libheif::heif")
        self.cpp_info.components["heif"].set_property("pkg_config_name", "libheif")
        self.cpp_info.components["heif"].requires = ["libde265::libde265"]
        if self.options.with_x265:
            self.cpp_info.components["heif"].requires.append("libx265::libx265")
        if self.options.with_libaomav1:
            self.cpp_info.components["heif"].requires.append("libaom-av1::libaom-av1")
        if self.options.get_safe("with_dav1d"):
            self.cpp_info.components["heif"].requires.append("dav1d::dav1d")
