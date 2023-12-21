from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import copy, get, replace_in_file, rm, rmdir
from conan.tools.microsoft import is_msvc, is_msvc_static_runtime
from conan.tools.scm import Version
import os

required_conan_version = ">=1.53.0"


class LibjpegTurboConan(ConanFile):
    name = "libjpeg-turbo"
    description = "SIMD-accelerated libjpeg-compatible JPEG codec library"
    license = ("IJG", "BSD-3-Clause", "Zlib")
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

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if Version(self.version) >= "3.0.0":
            del self.options.enable12bit
            del self.options.mem_src_dst

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

        if self.options.get_safe("enable12bit"):
            del self.options.java
            del self.options.turbojpeg
        if self.options.get_safe("enable12bit") or self.settings.os == "Emscripten":
            del self.options.SIMD
        if self.options.get_safe("enable12bit") or self.options.libjpeg7_compatibility or self.options.libjpeg8_compatibility:
            del self.options.arithmetic_encoder
            del self.options.arithmetic_decoder
        if self.options.libjpeg8_compatibility:
            self.options.rm_safe("mem_src_dst")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def validate(self):
        if self.options.get_safe("enable12bit") and (self.options.libjpeg7_compatibility or self.options.libjpeg8_compatibility):
            raise ConanInvalidConfiguration("12-bit samples is not allowed with libjpeg v7/v8 API/ABI")
        if self.options.get_safe("java") and not self.options.shared:
            raise ConanInvalidConfiguration("java wrapper requires shared libjpeg-turbo")
        if self.options.shared and is_msvc(self) and is_msvc_static_runtime(self):
            raise ConanInvalidConfiguration(f"{self.ref} shared can't be built with static vc runtime")

    def build_requirements(self):
        if self.options.get_safe("SIMD") and self.settings.arch in ["x86", "x86_64"]:
            self.tool_requires("nasm/2.15.05")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    @property
    def _is_arithmetic_encoding_enabled(self):
        return self.options.get_safe("arithmetic_encoder", False) or \
               self.options.libjpeg7_compatibility or self.options.libjpeg8_compatibility

    @property
    def _is_arithmetic_decoding_enabled(self):
        return self.options.get_safe("arithmetic_decoder", False) or \
               self.options.libjpeg7_compatibility or self.options.libjpeg8_compatibility

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()

        tc = CMakeToolchain(self)
        tc.variables["ENABLE_STATIC"] = not self.options.shared
        tc.variables["ENABLE_SHARED"] = self.options.shared
        tc.variables["WITH_SIMD"] = self.options.get_safe("SIMD", False)
        tc.variables["WITH_ARITH_ENC"] = self._is_arithmetic_encoding_enabled
        tc.variables["WITH_ARITH_DEC"] = self._is_arithmetic_decoding_enabled
        tc.variables["WITH_JPEG7"] = self.options.libjpeg7_compatibility
        tc.variables["WITH_JPEG8"] = self.options.libjpeg8_compatibility
        tc.variables["WITH_TURBOJPEG"] = self.options.get_safe("turbojpeg", False)
        tc.variables["WITH_JAVA"] = self.options.get_safe("java", False)
        if Version(self.version) < "3.0.0":
            tc.variables["WITH_MEM_SRCDST"] = self.options.get_safe("mem_src_dst", False)
            tc.variables["WITH_12BIT"] = self.options.enable12bit
        if is_msvc(self):
            tc.variables["WITH_CRT_DLL"] = True # avoid replacing /MD by /MT in compiler flags
        if Version(self.version) <= "2.1.0":
            tc.variables["CMAKE_MACOSX_BUNDLE"] = False # avoid configuration error if building for iOS/tvOS/watchOS
        tc.generate()

    def _patch_sources(self):
        # use standard GNUInstallDirs.cmake - custom one is broken
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"),
                              "include(cmakescripts/GNUInstallDirs.cmake)",
                              "include(GNUInstallDirs)")
        # do not override /MT by /MD if shared
        replace_in_file(self, os.path.join(self.source_folder, "sharedlib", "CMakeLists.txt"),
                              """string(REGEX REPLACE "/MT" "/MD" ${var} "${${var}}")""",
                              "")

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE.md", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "README.ijg", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        # remove unneeded directories
        rmdir(self, os.path.join(self.package_folder, "share"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "doc"))
        # remove binaries and pdb files
        for pattern_to_remove in ["cjpeg*", "djpeg*", "jpegtran*", "tjbench*", "wrjpgcom*", "rdjpgcom*", "*.pdb"]:
            rm(self, pattern_to_remove, os.path.join(self.package_folder, "bin"))

    def package_info(self):
        self.cpp_info.set_property("cmake_find_mode", "both")
        self.cpp_info.set_property("cmake_module_file_name", "JPEG")
        self.cpp_info.set_property("cmake_file_name", "libjpeg-turbo")

        cmake_target_suffix = "-static" if not self.options.shared else ""
        lib_suffix = "-static" if is_msvc(self) and not self.options.shared else ""

        self.cpp_info.components["jpeg"].set_property("cmake_module_target_name", "JPEG::JPEG")
        self.cpp_info.components["jpeg"].set_property("cmake_target_name", f"libjpeg-turbo::jpeg{cmake_target_suffix}")
        self.cpp_info.components["jpeg"].set_property("pkg_config_name", "libjpeg")
        self.cpp_info.components["jpeg"].libs = [f"jpeg{lib_suffix}"]

        if self.options.get_safe("turbojpeg"):
            self.cpp_info.components["turbojpeg"].set_property("cmake_target_name", f"libjpeg-turbo::turbojpeg{cmake_target_suffix}")
            self.cpp_info.components["turbojpeg"].set_property("pkg_config_name", "libturbojpeg")
            self.cpp_info.components["turbojpeg"].libs = [f"turbojpeg{lib_suffix}"]

        # TODO: to remove in conan v2
        self.cpp_info.names["cmake_find_package"] = "JPEG"
        self.cpp_info.names["cmake_find_package_multi"] = "libjpeg-turbo"
        self.cpp_info.components["jpeg"].names["cmake_find_package"] = "JPEG"
        self.cpp_info.components["jpeg"].names["cmake_find_package_multi"] = f"jpeg{cmake_target_suffix}"
        if self.options.get_safe("turbojpeg"):
            self.cpp_info.components["turbojpeg"].names["cmake_find_package"] = f"turbojpeg{cmake_target_suffix}"
            self.cpp_info.components["turbojpeg"].names["cmake_find_package_multi"] = f"turbojpeg{cmake_target_suffix}"
