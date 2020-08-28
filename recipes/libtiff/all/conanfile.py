from conans import ConanFile, CMake, tools
import os


class LibtiffConan(ConanFile):
    name = "libtiff"
    description = "Library for Tag Image File Format (TIFF)"
    url = "https://github.com/conan-io/conan-center-index"
    license = "MIT"
    homepage = "http://www.simplesystems.org/libtiff"
    topics = ("tiff", "image", "bigtiff", "tagged-image-file-format")
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake", "cmake_find_package"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False],
               "fPIC": [True, False],
               "lzma": [True, False],
               "jpeg": [True, False],
               "zlib": [True, False],
               "zstd": [True, False],
               "jbig": [True, False],
               "webp": [True, False],
               "cxx":  [True, False]}
    default_options = {"shared": False,
                       "fPIC": True,
                       "lzma": True,
                       "jpeg": True,
                       "zlib": True,
                       "zstd": True,
                       "jbig": True,
                       "webp": True,
                       "cxx":  True}
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
        if tools.Version(self.version) < "4.1.0":
            del self.options.webp
            del self.options.zstd

    def configure(self):
        if not self.options.cxx:
            del self.settings.compiler.libcxx
            del self.settings.compiler.cppstd

    def requirements(self):
        if self.options.zlib:
            self.requires("zlib/1.2.11")
        if self.options.lzma:
            self.requires("xz_utils/5.2.4")
        if self.options.jpeg:
            self.requires("libjpeg/9d")
        if self.options.jbig:
            self.requires("jbig/20160605")
        if self.options.get_safe("zstd"):
            self.requires("zstd/1.4.5")
        if self.options.get_safe("webp"):
            self.requires("libwebp/1.1.0")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("tiff-" + self.version, self._source_subfolder)

    def _patch_sources(self):
        if self.options.shared and self.settings.compiler == "Visual Studio":
            # https://github.com/Microsoft/vcpkg/blob/master/ports/tiff/fix-cxx-shared-libs.patch
            tools.replace_in_file(os.path.join(self._source_subfolder, "libtiff", "CMakeLists.txt"),
                                  r"set_target_properties(tiffxx PROPERTIES SOVERSION ${SO_COMPATVERSION})",
                                  r"set_target_properties(tiffxx PROPERTIES SOVERSION ${SO_COMPATVERSION} "
                                  r"WINDOWS_EXPORT_ALL_SYMBOLS ON)")
        cmakefile = os.path.join(self._source_subfolder, "CMakeLists.txt")
        if self.settings.os == "Windows" and self.settings.compiler != "Visual Studio":
            tools.replace_in_file(cmakefile,
                                  "find_library(M_LIBRARY m)",
                                  "if (NOT MINGW)\n  find_library(M_LIBRARY m)\nendif()")
            if tools.Version(self.version) < "4.0.9":
                tools.replace_in_file(cmakefile, "if (UNIX)", "if (UNIX OR MINGW)")
        tools.replace_in_file(cmakefile,
                              "add_subdirectory(tools)\nadd_subdirectory(test)\nadd_subdirectory(contrib)\nadd_subdirectory(build)\n"
                              "add_subdirectory(man)\nadd_subdirectory(html)", "")
        tools.replace_in_file(cmakefile, "LIBLZMA_LIBRARIES", "LibLZMA_LIBRARIES")

    def _configure_cmake(self):
        if not self._cmake:
            self._cmake = CMake(self)
            self._cmake.definitions["lzma"] = self.options.lzma
            self._cmake.definitions["jpeg"] = self.options.jpeg
            self._cmake.definitions["jbig"] = self.options.jbig
            self._cmake.definitions["zlib"] = self.options.zlib
            self._cmake.definitions["zstd"] = self.options.get_safe("zstd", False)
            self._cmake.definitions["webp"] = self.options.get_safe("webp", False)
            self._cmake.definitions["cxx"] = self.options.cxx
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
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        if self.options.cxx:
            self.cpp_info.libs.append("tiffxx")
        self.cpp_info.libs.append("tiff")
        if self.settings.os == "Windows" and self.settings.build_type == "Debug" and self.settings.compiler == "Visual Studio":
            self.cpp_info.libs = [lib + "d" for lib in self.cpp_info.libs]
        if self.options.shared and self.settings.os == "Windows" and self.settings.compiler != "Visual Studio":
            self.cpp_info.libs = [lib + ".dll" for lib in self.cpp_info.libs]
        if self.settings.os == "Linux":
            self.cpp_info.system_libs.append("m")
        self.cpp_info.names["cmake_find_package"] = "TIFF"
        self.cpp_info.names["cmake_find_package_multi"] = "TIFF"
        self.cpp_info.names["pkg_config"] = "libtiff-4"
