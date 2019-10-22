from conans import ConanFile, CMake, tools
import os
import shutil


class LibtiffConan(ConanFile):
    name = "libtiff"
    description = "Library for Tag Image File Format (TIFF)"
    url = "https://github.com/conan-io/conan-center-index"
    author = "Bincrafters <bincrafters@gmail.com>"
    license = "MIT"
    homepage = "http://www.simplesystems.org/libtiff"
    topics = ("tiff", "image", "bigtiff", "tagged-image-file-format")
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {'shared': False, 'fPIC': True}
    requires = "zlib/1.2.11"

    _source_subfolder = "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.remove("fPIC")
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename('tiff-' + self.version, self._source_subfolder)
        os.rename(os.path.join(self._source_subfolder, "CMakeLists.txt"),
                  os.path.join(self._source_subfolder, "CMakeListsOriginal.txt"))
        shutil.copy("CMakeLists.txt",
                    os.path.join(self._source_subfolder, "CMakeLists.txt"))

    def build(self):
        cmake = CMake(self)

        cmake.definitions['CMAKE_INSTALL_LIBDIR'] = 'lib'
        cmake.definitions['CMAKE_INSTALL_BINDIR'] = 'bin'
        cmake.definitions['CMAKE_INSTALL_INCLUDEDIR'] = 'include'

        cmake.definitions["lzma"] = False
        cmake.definitions["jpeg"] = False
        cmake.definitions["jbig"] = False
        if self.options.shared and self.settings.compiler == "Visual Studio":
            # https://github.com/Microsoft/vcpkg/blob/master/ports/tiff/fix-cxx-shared-libs.patch
            tools.replace_in_file(os.path.join(self._source_subfolder, 'libtiff', 'CMakeLists.txt'),
                                  r'set_target_properties(tiffxx PROPERTIES SOVERSION ${SO_COMPATVERSION})',
                                  r'set_target_properties(tiffxx PROPERTIES SOVERSION ${SO_COMPATVERSION} '
                                  r'WINDOWS_EXPORT_ALL_SYMBOLS ON)')

        if self.settings.os == "Windows" and self.settings.compiler != "Visual Studio":
            tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeListsOriginal.txt"),
                                      "find_library(M_LIBRARY m)",
                                      "if (NOT MINGW)\n  find_library(M_LIBRARY m)\nendif()")
            if self.version == '4.0.8':
                # only one occurence must be patched. fixed in 4.0.9
                tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeListsOriginal.txt"),
                                      "if (UNIX)",
                                      "if (UNIX OR MINGW)")

        tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeListsOriginal.txt"),
            "add_subdirectory(tools)\nadd_subdirectory(test)\nadd_subdirectory(contrib)\nadd_subdirectory(build)\n"
            "add_subdirectory(man)\nadd_subdirectory(html)", "")

        cmake.definitions["BUILD_SHARED_LIBS"] = self.options.shared
        cmake.configure(source_folder=self._source_subfolder)
        cmake.build()
        cmake.install()

    def package(self):
        self.copy("COPYRIGHT", src=self._source_subfolder, dst="licenses", ignore_case=True, keep_path=False)
        tools.rmdir(os.path.join(self.package_folder, 'lib', 'pkgconfig'))

    def package_info(self):
        self.cpp_info.libs = ["tiff", "tiffxx"]
        if self.settings.os == "Windows" and self.settings.build_type == "Debug" and self.settings.compiler == 'Visual Studio':
            self.cpp_info.libs = [lib+'d' for lib in self.cpp_info.libs]
        if self.options.shared and self.settings.os == "Windows" and self.settings.compiler != 'Visual Studio':
            self.cpp_info.libs = [lib+'.dll' for lib in self.cpp_info.libs]
        if self.settings.os == "Linux":
            self.cpp_info.libs.append("m")
        self.cpp_info.name = "TIFF"
