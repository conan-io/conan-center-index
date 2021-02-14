from conans import ConanFile, CMake, tools
import os
import shutil


class LeptonicaConan(ConanFile):
    name = "leptonica"
    url = "https://github.com/conan-io/conan-center-index"
    description = "Library containing software that is broadly useful for image processing and image analysis applications."
    topics = ("conan", "leptonica", "image", "multimedia", "format", "graphics")
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "cmake_find_package"
    homepage = "http://leptonica.org"
    license = "BSD 2-Clause"
    exports_sources = ["CMakeLists.txt"]

    options = {"shared": [True, False],
               "with_gif": [True, False],
               "with_jpeg": [True, False],
               "with_png": [True, False],
               "with_tiff": [True, False],
               "with_openjpeg": [True, False],
               "with_webp": [True, False],
               "fPIC": [True, False]
              }
    default_options = {'shared': False,
                       'with_gif': False,
                       'with_jpeg': True,
                       'with_png': True,
                       'with_tiff': True,
                       'with_openjpeg': True,
                       'with_webp': True,
                       'fPIC': True}

    _cmake = None
    _source_subfolder = "source_subfolder"

    def requirements(self):
        self.requires("zlib/1.2.11")
        if self.options.with_gif:
            self.requires("giflib/5.2.1")
        if self.options.with_jpeg:
            self.requires("libjpeg/9d")
        if self.options.with_png:
            self.requires("libpng/1.6.37")
        if self.options.with_tiff:
            self.requires("libtiff/4.2.0")
        if self.options.with_openjpeg:
            self.requires("openjpeg/2.4.0")
        if self.options.with_webp:
            self.requires("libwebp/1.1.0")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)
        # Leptonica is very sensitive to package layout
        # so use source directory same as _source_subfolder
        os.rename(os.path.join(self._source_subfolder, "CMakeLists.txt"),
                  os.path.join(self._source_subfolder, "CMakeListsOriginal.txt"))
        shutil.copy("CMakeLists.txt",
                    os.path.join(self._source_subfolder, "CMakeLists.txt"))

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        cmake = self._cmake = CMake(self)
        if self.version == '1.78.0':
            cmake.definitions['STATIC'] = not self.options.shared
        cmake.definitions['BUILD_PROG'] = False
        # avoid finding system libs
        cmake.definitions['CMAKE_DISABLE_FIND_PACKAGE_GIF'] = not self.options.with_gif
        cmake.definitions['CMAKE_DISABLE_FIND_PACKAGE_PNG'] = not self.options.with_png
        cmake.definitions['CMAKE_DISABLE_FIND_PACKAGE_TIFF'] = not self.options.with_tiff
        cmake.definitions['CMAKE_DISABLE_FIND_PACKAGE_JPEG'] = not self.options.with_jpeg

        cmake.definitions['SW_BUILD'] = False

        cmake.configure(source_folder=self._source_subfolder)
        return cmake

    def build(self):
        cmake_original = os.path.join(self._source_subfolder,
                                      "CMakeListsOriginal.txt")
        # disable pkgconfig
        tools.replace_in_file(cmake_original,
                              "if (PKG_CONFIG_FOUND)",
                              "if (FALSE)")

        # short out conditionals that don't respect
        # CMAKE_DISABLE_FIND_PACKAGE_x
        if not self.options.with_webp:
            tools.replace_in_file(cmake_original,
                                  "if(NOT WEBP)",
                                  "if(FALSE)")
            tools.replace_in_file(cmake_original,
                                  "if(NOT WEBPMUX)",
                                  "if(FALSE)")
        if not self.options.with_openjpeg:
            tools.replace_in_file(cmake_original,
                                  "if(NOT JP2K)",
                                  "if(FALSE)")

        # Remove detection of fmemopen() on macOS < 10.13
        # CheckFunctionExists will find it in the link library.
        # There's no error because it's not including the header with the
        # deprecation macros.
        if self.settings.os == 'Macos' and self.settings.os.version:
            if tools.Version(self.settings.os.version) < '10.13':
                configure_cmake = os.path.join(self._source_subfolder,
                                               'cmake',
                                               'Configure.cmake')
                tools.replace_in_file(configure_cmake,
                                      'set(functions_list\n    '
                                      'fmemopen\n    fstatat\n)',
                                      'set(functions_list\n    '
                                      'fstatat\n)')

        # upstream uses obsolete FOO_LIBRARY that is not generated
        # by cmake_find_package generator (upstream PR 456)
        if tools.Version(self.version) <= '1.78.0':
            for dep in ('GIF', 'TIFF', 'PNG', 'JPEG', 'ZLIB'):
                tools.replace_in_file(os.path.join(self._source_subfolder, "src", "CMakeLists.txt"),
                                      dep + "_LIBRARY",
                                      dep + "_LIBRARIES")

        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()

        self.copy(pattern="leptonica-license.txt", dst="licenses", src=self._source_subfolder)
        # remove pkgconfig
        tools.rmdir(os.path.join(self.package_folder, 'lib', 'pkgconfig'))
        # remove cmake
        tools.rmdir(os.path.join(self.package_folder, 'cmake'))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os == "Linux":
            self.cpp_info.system_libs = ["m"]
        self.cpp_info.names["cmake_find_package"] = "Leptonica"
        self.cpp_info.names["cmake_find_package_multi"] = "Leptonica"
        self.cpp_info.names['pkg_config'] = 'lept'
        self.cpp_info.includedirs.append(os.path.join("include", "leptonica"))
