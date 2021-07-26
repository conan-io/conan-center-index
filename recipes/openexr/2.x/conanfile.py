from conans import ConanFile, CMake, tools
import os


class OpenEXRConan(ConanFile):
    name = "openexr"
    description = "OpenEXR is a high dynamic-range (HDR) image file format developed by Industrial Light & " \
                  "Magic for use in computer imaging applications."
    topics = ("conan", "openexr", "hdr", "image", "picture")
    license = "BSD-3-Clause"
    homepage = "https://github.com/openexr/openexr"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    generators = "cmake", "cmake_find_package"
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
        self.requires("zlib/1.2.11")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("openexr-{}".format(self.version), self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["PYILMBASE_ENABLE"] = False
        self._cmake.definitions["OPENEXR_VIEWERS_ENABLE"] = False
        self._cmake.definitions["OPENEXR_BUILD_BOTH_STATIC_SHARED"] = False
        self._cmake.definitions["OPENEXR_BUILD_UTILS"] = False
        self._cmake.definitions["BUILD_TESTING"] = False
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def _patch_files(self):

        pkg_version = tools.Version(self.version)
        if pkg_version < "2.5.2" and self.settings.os == "Windows":
            # This fixes symlink creation on Windows.
            # OpenEXR's build system no longer creates symlinks on windows, starting with commit
            # 7f9e1b410de92de244329b614cf551b30bc30421 (included in 2.5.2).
            for lib in ("OpenEXR", "IlmBase"):
                tools.replace_in_file(os.path.join(self._source_subfolder,  lib, "config", "LibraryDefine.cmake"),
                                      "${CMAKE_COMMAND} -E chdir ${CMAKE_INSTALL_FULL_LIBDIR}",
                                      "${CMAKE_COMMAND} -E chdir ${CMAKE_INSTALL_FULL_BINDIR}")

        # Add  "_d" suffix to lib file names.
        for lib in ("OpenEXR", "IlmBase"):
            if self.settings.build_type == "Debug":
                tools.replace_in_file(os.path.join(self._source_subfolder,  lib, "config", "LibraryDefine.cmake"),
                                      "set(verlibname ${CMAKE_SHARED_LIBRARY_PREFIX}${libname}${@LIB@_LIB_SUFFIX}${CMAKE_SHARED_LIBRARY_SUFFIX})".replace("@LIB@", lib.upper()),
                                      "set(verlibname ${CMAKE_SHARED_LIBRARY_PREFIX}${libname}${@LIB@_LIB_SUFFIX}_d${CMAKE_SHARED_LIBRARY_SUFFIX})".replace("@LIB@", lib.upper()))
                tools.replace_in_file(os.path.join(self._source_subfolder,  lib, "config", "LibraryDefine.cmake"),
                                      "set(baselibname ${CMAKE_SHARED_LIBRARY_PREFIX}${libname}${CMAKE_SHARED_LIBRARY_SUFFIX})",
                                      "set(baselibname ${CMAKE_SHARED_LIBRARY_PREFIX}${libname}_d${CMAKE_SHARED_LIBRARY_SUFFIX})")

    def build(self):
        self._patch_files()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE.md", src=self._source_subfolder, dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "share"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "OpenEXR"
        self.cpp_info.names["cmake_find_package_multi"] = "OpenEXR"
        self.cpp_info.names["pkg_config"] = "OpenEXR"
        parsed_version = self.version.split(".")
        lib_suffix = "-{}_{}".format(parsed_version[0], parsed_version[1])
        if self.settings.build_type == "Debug":
            lib_suffix += "_d"

        self.cpp_info.libs = ["IlmImf{}".format(lib_suffix),
                              "IlmImfUtil{}".format(lib_suffix),
                              "IlmThread{}".format(lib_suffix),
                              "Imath{}".format(lib_suffix),
                              "Half{}".format(lib_suffix),
                              "IexMath{}".format(lib_suffix),
                              "Iex{}".format(lib_suffix)]

        self.cpp_info.includedirs = [os.path.join("include", "OpenEXR"), "include"]
        if self.options.shared and self.settings.os == "Windows":
            self.cpp_info.defines.append("OPENEXR_DLL")

        if self.settings.os == "Linux":
            self.cpp_info.system_libs.append("pthread")

        stdlib = tools.stdcpp_library(self)
        if not self.options.shared and stdlib:
            self.cpp_info.system_libs.append(stdlib)
