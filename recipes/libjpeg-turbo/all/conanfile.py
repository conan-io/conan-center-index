import os
import glob
from conans import ConanFile, CMake, tools


class LibjpegTurboConan(ConanFile):
    name = "libjpeg-turbo"
    description = "SIMD-accelerated libjpeg-compatible JPEG codec library"
    topics = ("conan", "jpeg", "libjpeg", "image", "multimedia", "format", "graphics")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://libjpeg-turbo.org"
    license = "BSD-3-Clause, Zlib"
    provides = "libjpeg"
    exports_sources = "CMakeLists.txt"
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False],
               "fPIC": [True, False],
               "SIMD": [True, False],
               "arithmetic_encoder": [True, False],
               "arithmetic_decoder": [True, False],
               "libjpeg7_compatibility": [True, False],
               "libjpeg8_compatibility": [True, False],
               "mem_src_dst": [True, False],
               "turbojpeg": [True, False],
               "java": [True, False],
               "enable12bit": [True, False]}
    default_options = {"shared": False,
                       "fPIC": True,
                       "SIMD": True,
                       "arithmetic_encoder": True,
                       "arithmetic_decoder": True,
                       "libjpeg7_compatibility": True,
                       "libjpeg8_compatibility": True,
                       "mem_src_dst": True,
                       "turbojpeg": True,
                       "java": False,
                       "enable12bit": False}

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd
        if self.options.shared:
            del self.options.fPIC
        if self.settings.os == "Emscripten":
            del self.options.SIMD

    def build_requirements(self):
        self.build_requires("nasm/2.14")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename(self.name + "-" + self.version, self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self, set_cmake_flags=True)
        self._cmake.definitions["ENABLE_STATIC"] = not self.options.shared
        self._cmake.definitions["ENABLE_SHARED"] = self.options.shared
        self._cmake.definitions["WITH_SIMD"] = self.options.get_safe("SIMD", False)
        self._cmake.definitions["WITH_ARITH_ENC"] = self.options.arithmetic_encoder
        self._cmake.definitions["WITH_ARITH_DEC"] = self.options.arithmetic_decoder
        self._cmake.definitions["WITH_JPEG7"] = self.options.libjpeg7_compatibility
        self._cmake.definitions["WITH_JPEG8"] = self.options.libjpeg8_compatibility
        self._cmake.definitions["WITH_MEM_SRCDST"] = self.options.mem_src_dst
        self._cmake.definitions["WITH_TURBOJPEG"] = self.options.turbojpeg
        self._cmake.definitions["WITH_JAVA"] = self.options.java
        self._cmake.definitions["WITH_12BIT"] = self.options.enable12bit
        if self.settings.compiler == "Visual Studio":
            self._cmake.definitions["WITH_CRT_DLL"] = True # avoid replacing /MD by /MT in compiler flags
        self._cmake.configure()
        return self._cmake

    def _patch_sources(self):
        # use standard GNUInstallDirs.cmake - custom one is broken
        tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"),
                              "include(cmakescripts/GNUInstallDirs.cmake)",
                              "include(GNUInstallDirs)")
        # do not override /MT by /MD if shared
        tools.replace_in_file(os.path.join(self._source_subfolder, "sharedlib", "CMakeLists.txt"),
                              """string(REGEX REPLACE "/MT" "/MD" ${var} "${${var}}")""",
                              "")

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE.md", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        # remove unneeded directories
        tools.rmdir(os.path.join(self.package_folder, "share"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "doc"))
        # remove binaries and pdb files
        for pattern_to_remove in ["cjpeg*", "djpeg*", "jpegtran*", "tjbench*", "wrjpgcom*", "rdjpgcom*", "*.pdb"]:
            for bin_file in glob.glob(os.path.join(self.package_folder, "bin", pattern_to_remove)):
                os.remove(bin_file)

    def package_info(self):
        self.cpp_info.components["jpeg"].names["pkg_config"] = "libjpeg"
        self.cpp_info.components["jpeg"].libs = [self._lib_name("jpeg")]
        if self.options.turbojpeg:
            self.cpp_info.components["turbojpeg"].names["pkg_config"] = "libturbojpeg"
            self.cpp_info.components["turbojpeg"].libs = [self._lib_name("turbojpeg")]

    def _lib_name(self, name):
        if self.settings.compiler == "Visual Studio" and not self.options.shared:
            return name + "-static"
        return name
