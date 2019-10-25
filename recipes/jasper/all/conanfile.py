import os
from conans import ConanFile, CMake, tools


class JasperConan(ConanFile):
    name = "jasper"
    license = "JasPer License Version 2.0"
    homepage = "https://github.com/mdadams/jasper"
    url = "https://github.com/conan-io/conan-center-index"
    topics = ("conan", "jasper", "tool-kit", "coding")
    description = "JasPer Image Processing/Coding Tool Kit"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False],
               "fPIC": [True, False],
               "jpegturbo": [True, False]}
    default_options = {'shared': False, 'fPIC': True, 'jpegturbo': False}
    generators = "cmake"
    _source_subfolder = "source_subfolder"

    def requirements(self):
        if self.options.jpegturbo:
            self.requires.add('libjpeg-turbo/1.5.2')
        else:
            self.requires.add('libjpeg/9c')

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        del self.settings.compiler.cppstd
        del self.settings.compiler.libcxx

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = "{}-version-{}".format(self.name, self.version)
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["JAS_ENABLE_DOC"] = False
        cmake.definitions["JAS_ENABLE_PROGRAMS"] = False
        cmake.definitions["JAS_ENABLE_SHARED"] = self.options.shared
        cmake.definitions["JAS_LIBJPEG_REQUIRED"] = "REQUIRED"
        cmake.definitions["JAS_ENABLE_OPENGL"] = False
        cmake.configure(source_folder=self._source_subfolder)
        return cmake

    def _patch_cmake(self):
        cmake_file = os.path.join(self._source_subfolder, "CMakeLists.txt")
        tools.replace_in_file(cmake_file,
                              "project(JasPer LANGUAGES C)",
                              """project(JasPer LANGUAGES C)
                                 include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
                                 conan_basic_setup()""")

    def build(self):
        self._patch_cmake()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "share"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        for dll in ['concrt140.dll', 'msvcp140.dll', 'vcruntime140.dll']:
            dll_file = os.path.join(self.package_folder, 'bin', dll)
            if os.path.isfile(dll_file):
                os.unlink(dll_file)

    def package_info(self):
        self.cpp_info.libs = ["jasper"]
        if self.settings.os == "Linux":
            self.cpp_info.libs.append("m")
