from conan import ConanFile, tools
from conans import CMake
from conan.errors import ConanInvalidConfiguration
from conan.tools.microsoft import is_msvc
import os
import functools

required_conan_version = ">=1.45.0"


class LibjpegTurboConan(ConanFile):
    name = "libjpeg-turbo"
    description = "SIMD-accelerated libjpeg-compatible JPEG codec library"
    license = "BSD-3-Clause, Zlib"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://libjpeg-turbo.org"
    topics = ("jpeg", "libjpeg", "image", "multimedia", "format", "graphics")
    provides = "libjpeg"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "SIMD": [True, False],
        "arithmetic_encoder": [True, False],
        "arithmetic_decoder": [True, False],
        "libjpeg7_compatibility": [True, False],
        "libjpeg8_compatibility": [True, False],
        "mem_src_dst": [True, False],
        "turbojpeg": [True, False],
        "java": [True, False],
        "enable12bit": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "SIMD": True,
        "arithmetic_encoder": True,
        "arithmetic_decoder": True,
        "libjpeg7_compatibility": True,
        "libjpeg8_compatibility": True,
        "mem_src_dst": True,
        "turbojpeg": True,
        "java": False,
        "enable12bit": False,
    }
    generators = "cmake"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def export_sources(self):
        self.copy("CMakeLists.txt")
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd
        if self.options.shared:
            del self.options.fPIC

        if self.options.enable12bit:
            del self.options.java
            del self.options.turbojpeg
        if self.options.enable12bit or self.settings.os == "Emscripten":
            del self.options.SIMD
        if self.options.enable12bit or self.options.libjpeg7_compatibility or self.options.libjpeg8_compatibility:
            del self.options.arithmetic_encoder
            del self.options.arithmetic_decoder
        if self.options.libjpeg8_compatibility:
            del self.options.mem_src_dst

    def validate(self):
        if self.options.enable12bit and (self.options.libjpeg7_compatibility or self.options.libjpeg8_compatibility):
            raise ConanInvalidConfiguration("12-bit samples is not allowed with libjpeg v7/v8 API/ABI")
        if self.options.get_safe("java", False) and not self.options.shared:
            raise ConanInvalidConfiguration("java wrapper requires shared libjpeg-turbo")
        if is_msvc(self) and self.options.shared and str(self.settings.compiler.runtime).startswith("MT"):
            raise ConanInvalidConfiguration("shared libjpeg-turbo can't be built with MT or MTd")

    @property
    def _is_arithmetic_encoding_enabled(self):
        return self.options.get_safe("arithmetic_encoder", False) or \
               self.options.libjpeg7_compatibility or self.options.libjpeg8_compatibility

    @property
    def _is_arithmetic_decoding_enabled(self):
        return self.options.get_safe("arithmetic_decoder", False) or \
               self.options.libjpeg7_compatibility or self.options.libjpeg8_compatibility

    def build_requirements(self):
        if self.options.get_safe("SIMD") and self.settings.arch in ["x86", "x86_64"]:
            self.build_requires("nasm/2.14")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self, set_cmake_flags=True)
        cmake.definitions["ENABLE_STATIC"] = not self.options.shared
        cmake.definitions["ENABLE_SHARED"] = self.options.shared
        cmake.definitions["WITH_SIMD"] = self.options.get_safe("SIMD", False)
        cmake.definitions["WITH_ARITH_ENC"] = self._is_arithmetic_encoding_enabled
        cmake.definitions["WITH_ARITH_DEC"] = self._is_arithmetic_decoding_enabled
        cmake.definitions["WITH_JPEG7"] = self.options.libjpeg7_compatibility
        cmake.definitions["WITH_JPEG8"] = self.options.libjpeg8_compatibility
        cmake.definitions["WITH_MEM_SRCDST"] = self.options.get_safe("mem_src_dst", False)
        cmake.definitions["WITH_TURBOJPEG"] = self.options.get_safe("turbojpeg", False)
        cmake.definitions["WITH_JAVA"] = self.options.get_safe("java", False)
        cmake.definitions["WITH_12BIT"] = self.options.enable12bit
        if is_msvc(self):
            cmake.definitions["WITH_CRT_DLL"] = True # avoid replacing /MD by /MT in compiler flags

        if tools.Version(self.version) <= "2.1.0":
            cmake.definitions["CMAKE_MACOSX_BUNDLE"] = False # avoid configuration error if building for iOS/tvOS/watchOS

        if tools.cross_building(self):
            # TODO: too specific and error prone, should be delegated to a conan helper function
            cmake_system_processor = {
                "armv8": "aarch64",
                "armv8.3": "aarch64",
            }.get(str(self.settings.arch), str(self.settings.arch))
            cmake.definitions["CONAN_LIBJPEG_SYSTEM_PROCESSOR"] = cmake_system_processor

        cmake.configure()
        return cmake

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)

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
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "doc"))
        # remove binaries and pdb files
        for pattern_to_remove in ["cjpeg*", "djpeg*", "jpegtran*", "tjbench*", "wrjpgcom*", "rdjpgcom*", "*.pdb"]:
            tools.remove_files_by_mask(os.path.join(self.package_folder, "bin"), pattern_to_remove)

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "libjpeg-turbo")

        cmake_target_suffix = "-static" if not self.options.shared else ""
        lib_suffix = "-static" if is_msvc(self) and not self.options.shared else ""

        self.cpp_info.components["jpeg"].set_property("cmake_target_name", "libjpeg-turbo::jpeg{}".format(cmake_target_suffix))
        self.cpp_info.components["jpeg"].set_property("pkg_config_name", "libjpeg")
        self.cpp_info.components["jpeg"].names["cmake_find_package"] = "jpeg" + cmake_target_suffix
        self.cpp_info.components["jpeg"].names["cmake_find_package_multi"] = "jpeg" + cmake_target_suffix
        self.cpp_info.components["jpeg"].libs = ["jpeg" + lib_suffix]

        if self.options.get_safe("turbojpeg"):
            self.cpp_info.components["turbojpeg"].set_property("cmake_target_name", "libjpeg-turbo::turbojpeg{}".format(cmake_target_suffix))
            self.cpp_info.components["turbojpeg"].set_property("pkg_config_name", "libturbojpeg")
            self.cpp_info.components["turbojpeg"].names["cmake_find_package"] = "turbojpeg" + cmake_target_suffix
            self.cpp_info.components["turbojpeg"].names["cmake_find_package_multi"] = "turbojpeg" + cmake_target_suffix
            self.cpp_info.components["turbojpeg"].libs = ["turbojpeg" + lib_suffix]
