import os
import shutil
import glob
from conans import ConanFile, CMake, tools


class LibjpegTurboConan(ConanFile):
    name = "libjpeg-turbo"
    description = "SIMD-accelerated libjpeg-compatible JPEG codec library"
    topics = ("conan", "jpeg", "libjpeg", "image", "multimedia", "format", "graphics")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://libjpeg-turbo.org"
    license = "BSD-3-Clause, Zlib"
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

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def build_requirements(self):
        self.build_requires("nasm/2.14")

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd
        if self.settings.compiler == "Visual Studio":
            self.options.remove("fPIC")
        if self.settings.os == "Emscripten":
            del self.options.SIMD

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename(self.name + "-" + self.version, self._source_subfolder)

    @property
    def _simd(self):
        if self.settings.os == "Emscripten":
            return False
        return self.options.SIMD

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self, set_cmake_flags=True)
        self._cmake.definitions["ENABLE_STATIC"] = not self.options.shared
        self._cmake.definitions["ENABLE_SHARED"] = self.options.shared
        self._cmake.definitions["WITH_SIMD"] = self._simd
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
        self._cmake.configure(build_folder=self._build_subfolder)
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
        cmake = self._configure_cmake()
        cmake.install()
        # remove unneeded directories
        tools.rmdir(os.path.join(self.package_folder, "share"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "doc"))

        # remove binaries
        for bin_program in ["cjpeg", "djpeg", "jpegtran", "tjbench", "wrjpgcom", "rdjpgcom"]:
            for ext in ["", ".exe"]:
                try:
                    os.remove(os.path.join(self.package_folder, "bin", bin_program+ext))
                except OSError:
                    pass
        for pdb_file in glob.glob(os.path.join(self.package_folder, "bin", "*.pdb")):
            os.unlink(pdb_file)

        self.copy("license*", src=self._source_subfolder, dst="licenses", ignore_case=True, keep_path=False)

    def package_info(self):
        if self.settings.compiler == "Visual Studio":
            if self.options.shared:
                self.cpp_info.libs = ["jpeg", "turbojpeg"]
            else:
                self.cpp_info.libs = ["jpeg-static", "turbojpeg-static"]
        else:
            self.cpp_info.libs = ["jpeg", "turbojpeg"]
