import os
from conans import ConanFile, tools, CMake


class LibgdConan(ConanFile):
    name = "libgd"
    license = "https://github.com/libgd/libgd/blob/master/COPYING"
    url = "https://github.com/conan-io/conan-center-index"
    description = "GD is an open source code library for the dynamic creation of images by programmers."
    topics = ("images", "graphics")
    settings = "os", "compiler", "build_type", "arch"
    homepage = "https://libgd.github.io"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False}
    generators = "cmake"
    requires = "zlib/1.2.11"

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.remove("fPIC")

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename('libgd-' + self.version, self._source_subfolder)
        tools.replace_in_file(
            os.path.join(
                self._source_subfolder,
                "CMakeLists.txt"),
            "CMAKE_MINIMUM_REQUIRED(VERSION 2.6 FATAL_ERROR)",
            '''cmake_minimum_required (VERSION 3.6 FATAL_ERROR)
PROJECT(GD C)
include(${CMAKE_BINARY_DIR}/../conanbuildinfo.cmake)
conan_basic_setup()''')
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
	target_link_libraries(${GD_LIB} ${LIBGD_DEP_LIBS})''',
            '''if (NOT WIN32)
    list(APPEND LIBGD_DEP_LIBS  m)
endif()
if (BUILD_SHARED_LIBS)
	target_link_libraries(${GD_LIB} ${LIBGD_DEP_LIBS})
''')

    def build(self):
        cmake = CMake(self)
        cmake.definitions['BUILD_STATIC_LIBS'] = not self.options.shared
        cmake.definitions["ZLIB_LIBRARY"] = self.deps_cpp_info["zlib"].libs[0]
        cmake.definitions["ZLIB_INCLUDE_DIR"] = self.deps_cpp_info["zlib"].include_paths[0]
        cmake.configure(
            source_folder=self._source_subfolder,
            build_folder=self._build_subfolder)
        cmake.build()
        cmake.install()

    def package(self):
        self.copy("COPYING", src=self._source_subfolder, dst="licenses", ignore_case=True, keep_path=False)
        tools.rmdir(os.path.join(self.package_folder, 'share'))
        self.copy("*", src="bin", dst="bin")
        self.copy("*", src="lib", dst="lib")
        self.copy("entities.h", dst="include", src="src")
        self.copy("gd.h", dst="include", src="src")
        self.copy("gd_color_map.h", dst="include", src="src")
        self.copy("gd_errors.h", dst="include", src="src")
        self.copy("gd_io.h", dst="include", src="src")
        self.copy("gdcache.h", dst="include", src="src")
        self.copy("gdfontg.h", dst="include", src="src")
        self.copy("gdfontl.h", dst="include", src="src")
        self.copy("gdfontmb.h", dst="include", src="src")
        self.copy("gdfonts.h", dst="include", src="src")
        self.copy("gdfontt.h", dst="include", src="src")
        self.copy("gdfx.h", dst="include", src="src")
        self.copy("gdpp.h", dst="include", src="src")

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if not self.options.shared:
            self.cpp_info.defines.append('NONDLL')
            self.cpp_info.defines.append('BGDWIN32')
