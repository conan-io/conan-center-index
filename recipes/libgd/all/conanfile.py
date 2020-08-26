import os
from conans import ConanFile, tools, CMake


class LibgdConan(ConanFile):
    name = "libgd"
    license = "https://github.com/libgd/libgd/blob/master/COPYING"
    url = "https://github.com/conan-io/conan-center-index"
    description = ("GD is an open source code library for the dynamic "
                   "creation of images by programmers.")
    topics = ("images", "graphics")
    settings = "os", "compiler", "build_type", "arch"
    homepage = "https://libgd.github.io"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    generators = "cmake"
    requires = "zlib/1.2.11"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        for name in ['libgd-', 'libgd-gd-']:
            unpacked = name + self.version
            if os.path.exists(unpacked):
                os.rename(unpacked, self._source_subfolder)
                break
        else:
            raise RuntimeError('Did not find the unpacked archive')
        tools.replace_in_file(
            os.path.join(
                self._source_subfolder,
                "CMakeLists.txt"),
            "SET(PACKAGE GD)",
            '''cmake_minimum_required (VERSION 3.6 FATAL_ERROR)
PROJECT(GD C)
include(${CMAKE_BINARY_DIR}/../conanbuildinfo.cmake)
conan_basic_setup()
SET(PACKAGE GD)''')
        tools.replace_in_file(
            os.path.join(
                self._source_subfolder,
                "CMakeLists.txt"),
            'PROJECT(GD)',
            '# moved: PROJECT(GD)')
        tools.replace_in_file(
            os.path.join(
                self._source_subfolder,
                "CMakeLists.txt"),
            'if(NOT MINGW AND MSVC_VERSION GREATER 1399)',
            'if (BUILD_STATIC_LIBS AND WIN32 AND NOT MINGW AND NOT MSYS)')
        tools.replace_in_file(
            os.path.join(
                self._source_subfolder,
                "src",
                "CMakeLists.txt"),
            '''if (BUILD_SHARED_LIBS)
\ttarget_link_libraries(${GD_LIB} ${LIBGD_DEP_LIBS})''',
            '''if (NOT WIN32)
    list(APPEND LIBGD_DEP_LIBS  m)
endif()
if (BUILD_SHARED_LIBS)
\ttarget_link_libraries(${GD_LIB} ${LIBGD_DEP_LIBS})
''')

    def build(self):
        cmake = CMake(self)
        cmake.definitions['BUILD_STATIC_LIBS'] = not self.options.shared
        zlib_info = self.deps_cpp_info["zlib"]
        cmake.definitions["ZLIB_LIBRARY"] = zlib_info.libs[0]
        cmake.definitions["ZLIB_INCLUDE_DIR"] = zlib_info.include_paths[0]
        cmake.configure(
            source_folder=self._source_subfolder,
            build_folder=self._build_subfolder)
        cmake.build()
        cmake.install()

    def package(self):
        self.copy("COPYING", src=self._source_subfolder, dst="licenses",
                  ignore_case=True, keep_path=False)
        tools.rmdir(os.path.join(self.package_folder, 'share'))
        tools.rmdir(os.path.join(self.package_folder, 'lib', 'pkgconfig'))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if not self.options.shared:
            self.cpp_info.defines.append('NONDLL')
            self.cpp_info.defines.append('BGDWIN32')
