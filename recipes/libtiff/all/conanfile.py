from conan.tools.files import get, rename, rmdir
from conan.tools.microsoft import is_msvc
from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
from conans.tools import Version
import os

required_conan_version = ">=1.47.0"


class LibtiffConan(ConanFile):
    name = "libtiff"
    description = "Library for Tag Image File Format (TIFF)"
    url = "https://github.com/conan-io/conan-center-index"
    license = "MIT"
    homepage = "http://www.simplesystems.org/libtiff"
    topics = ("tiff", "image", "bigtiff", "tagged-image-file-format")

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "lzma": [True, False],
        "jpeg": [False, "libjpeg-turbo", "libjpeg"],
        "zlib": [True, False],
        "libdeflate": [True, False],
        "zstd": [True, False],
        "jbig": [True, False],
        "webp": [True, False],
        "cxx":  [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "lzma": True,
        "jpeg": "libjpeg",
        "zlib": True,
        "libdeflate": True,
        "zstd": True,
        "jbig": True,
        "webp": True,
        "cxx":  True,
    }

    generators = "cmake", "cmake_find_package"
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    @property
    def _has_webp_option(self):
        return Version(self.version) >= "4.0.10"

    @property
    def _has_zstd_option(self):
        return Version(self.version) >= "4.0.10"

    @property
    def _has_libdeflate_option(self):
        return Version(self.version) >= "4.2.0"

    def export_sources(self):
        self.copy("CMakeLists.txt")
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if not self._has_webp_option:
            del self.options.webp
        if not self._has_zstd_option:
            del self.options.zstd
        if not self._has_libdeflate_option:
            del self.options.libdeflate

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        if not self.options.cxx:
            del self.settings.compiler.libcxx
            del self.settings.compiler.cppstd

    def requirements(self):
        if self.options.zlib:
            self.requires("zlib/1.2.12")
        if self.options.get_safe("libdeflate"):
            self.requires("libdeflate/1.12")
        if self.options.lzma:
            self.requires("xz_utils/5.2.5")
        if self.options.jpeg == "libjpeg":
            self.requires("libjpeg/9d")
        if self.options.jpeg == "libjpeg-turbo":
            self.requires("libjpeg-turbo/2.1.3")
        if self.options.jbig:
            self.requires("jbig/20160605")
        if self.options.get_safe("zstd"):
            self.requires("zstd/1.5.2")
        if self.options.get_safe("webp"):
            self.requires("libwebp/1.2.3")

    def validate(self):
        if self.options.get_safe("libdeflate") and not self.options.zlib:
            raise ConanInvalidConfiguration("libtiff:libdeflate=True requires libtiff:zlib=True")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)

        # Rename the generated Findjbig.cmake and Findzstd.cmake to avoid case insensitive conflicts with FindJBIG.cmake and FindZSTD.cmake on Windows
        if Version(self.version) >= "4.3.0":
            if self.options.jbig:
                rename(self, "Findjbig.cmake", "ConanFindjbig.cmake")
            else:
                os.remove(os.path.join(self.build_folder, self._source_subfolder, "cmake", "FindJBIG.cmake"))
            if self.options.zstd:
                rename(self, "Findzstd.cmake", "ConanFindzstd.cmake")
            else:
                os.remove(os.path.join(self.build_folder, self._source_subfolder, "cmake", "FindZSTD.cmake"))

        if self.options.shared and is_msvc(self):
            # https://github.com/Microsoft/vcpkg/blob/master/ports/tiff/fix-cxx-shared-libs.patch
            tools.replace_in_file(os.path.join(self._source_subfolder, "libtiff", "CMakeLists.txt"),
                                  r"set_target_properties(tiffxx PROPERTIES SOVERSION ${SO_COMPATVERSION})",
                                  r"set_target_properties(tiffxx PROPERTIES SOVERSION ${SO_COMPATVERSION} "
                                  r"WINDOWS_EXPORT_ALL_SYMBOLS ON)")
        cmakefile = os.path.join(self._source_subfolder, "CMakeLists.txt")
        if self.settings.os == "Windows" and not is_msvc(self):
            if Version(self.version) < "4.2.0":
                tools.replace_in_file(cmakefile,
                                    "find_library(M_LIBRARY m)",
                                    "if (NOT MINGW)\n  find_library(M_LIBRARY m)\nendif()")
            if Version(self.version) < "4.0.9":
                tools.replace_in_file(cmakefile, "if (UNIX)", "if (UNIX OR MINGW)")
        tools.replace_in_file(cmakefile,
                              "add_subdirectory(tools)\nadd_subdirectory(test)\nadd_subdirectory(contrib)\nadd_subdirectory(build)\n"
                              "add_subdirectory(man)\nadd_subdirectory(html)", "")

    def _configure_cmake(self):
        if not self._cmake:
            self._cmake = CMake(self)
            self._cmake.definitions["lzma"] = self.options.lzma
            self._cmake.definitions["jpeg"] = self.options.jpeg != False
            self._cmake.definitions["jbig"] = self.options.jbig
            self._cmake.definitions["zlib"] = self.options.zlib
            if self._has_libdeflate_option:
                self._cmake.definitions["libdeflate"] = self.options.libdeflate
                if self.options.libdeflate:
                    if Version(self.version) < "4.3.0":
                        self._cmake.definitions["DEFLATE_NAMES"] = self.deps_cpp_info["libdeflate"].libs[0]
            if self._has_zstd_option:
                self._cmake.definitions["zstd"] = self.options.zstd
            if self._has_webp_option:
                self._cmake.definitions["webp"] = self.options.webp
            self._cmake.definitions["cxx"] = self.options.cxx

            # Workaround for cross-build to at least iOS/tvOS/watchOS,
            # when dependencies like libdeflate, jbig and zstd are found with find_path() and find_library()
            # see https://github.com/conan-io/conan-center-index/issues/6637
            if tools.cross_building(self):
                self._cmake.definitions["CMAKE_FIND_ROOT_PATH_MODE_INCLUDE"] = "BOTH"
                self._cmake.definitions["CMAKE_FIND_ROOT_PATH_MODE_LIBRARY"] = "BOTH"

            self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("COPYRIGHT", src=self._source_subfolder, dst="licenses", ignore_case=True, keep_path=False)
        cmake = self._configure_cmake()
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.set_property("cmake_find_mode", "both")
        self.cpp_info.set_property("cmake_file_name", "TIFF")
        self.cpp_info.set_property("cmake_target_name", "TIFF::TIFF")
        self.cpp_info.set_property("pkg_config_name", "libtiff-{}".format(Version(self.version).major))
        if self.options.cxx:
            self.cpp_info.libs.append("tiffxx")
        self.cpp_info.libs.append("tiff")
        if self.settings.os == "Windows" and self.settings.build_type == "Debug" and is_msvc(self):
            self.cpp_info.libs = [lib + "d" for lib in self.cpp_info.libs]
        if self.options.shared and self.settings.os == "Windows" and not is_msvc(self):
            self.cpp_info.libs = [lib + ".dll" for lib in self.cpp_info.libs]
        if self.settings.os in ["Linux", "Android", "FreeBSD", "SunOS", "AIX"]:
            self.cpp_info.system_libs.append("m")

        # TODO: to remove in conan v2 once cmake_find_package* & pkg_config generators removed
        self.cpp_info.names["cmake_find_package"] = "TIFF"
        self.cpp_info.names["cmake_find_package_multi"] = "TIFF"
        self.cpp_info.names["pkg_config"] = "libtiff-{}".format(Version(self.version).major)
