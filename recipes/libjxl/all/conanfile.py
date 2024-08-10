import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import cross_building, stdcpp_library, check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import copy, get, rmdir, save, rm, replace_in_file
from conan.tools.gnu import PkgConfigDeps
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version

required_conan_version = ">=1.53.0"


class LibjxlConan(ConanFile):
    name = "libjxl"
    description = "JPEG XL image format reference implementation"
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/libjxl/libjxl"
    topics = ("image", "jpeg-xl", "jxl", "jpeg")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "avx512": [True, False],
        "avx512_spr": [True, False],
        "avx512_zen4": [True, False],
        "with_tcmalloc": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "avx512": False,
        "avx512_spr": False,
        "avx512_zen4": False,
        "with_tcmalloc": False,
    }

    def export_sources(self):
        copy(self, "conan_deps.cmake", self.recipe_folder, os.path.join(self.export_sources_folder, "src"))

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if self.settings.arch not in ["x86", "x86_64"] or Version(self.version) < "0.9":
            del self.options.avx512
            del self.options.avx512_spr
            del self.options.avx512_zen4
        # https://github.com/libjxl/libjxl/blob/v0.9.1/CMakeLists.txt#L52-L59
        if self.settings.os in ["Linux", "FreeBSD"] and self.settings.arch == "x86_64":
            self.options.with_tcmalloc = True

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("brotli/1.1.0")
        self.requires("highway/1.1.0")
        self.requires("lcms/2.16")
        if self.options.with_tcmalloc:
            self.requires("gperftools/2.15")

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, 11)

    def build_requirements(self):
        # Require newer CMake, which allows INCLUDE_DIRECTORIES to be set on INTERFACE targets
        # Also, v0.9+ require CMake 3.16
        self.tool_requires("cmake/[>=3.19 <4]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        VirtualBuildEnv(self).generate()

        tc = CMakeToolchain(self)
        tc.variables["CMAKE_PROJECT_LIBJXL_INCLUDE"] = "conan_deps.cmake"
        tc.variables["BUILD_TESTING"] = False
        tc.variables["JPEGXL_STATIC"] = False
        tc.variables["JPEGXL_BUNDLE_LIBPNG"] = False
        tc.variables["JPEGXL_ENABLE_BENCHMARK"] = False
        tc.variables["JPEGXL_ENABLE_DOXYGEN"] = False
        tc.variables["JPEGXL_ENABLE_EXAMPLES"] = False
        tc.variables["JPEGXL_ENABLE_JNI"] = False
        tc.variables["JPEGXL_ENABLE_MANPAGES"] = False
        tc.variables["JPEGXL_ENABLE_OPENEXR"] = False
        tc.variables["JPEGXL_ENABLE_PLUGINS"] = False
        tc.variables["JPEGXL_ENABLE_SJPEG"] = False
        tc.variables["JPEGXL_ENABLE_SKCMS"] = False
        tc.variables["JPEGXL_ENABLE_TCMALLOC"] = self.options.with_tcmalloc
        tc.variables["JPEGXL_ENABLE_VIEWERS"] = False
        tc.variables["JPEGXL_ENABLE_TOOLS"] = False
        tc.variables["JPEGXL_FORCE_SYSTEM_BROTLI"] = True
        tc.variables["JPEGXL_FORCE_SYSTEM_GTEST"] = True
        tc.variables["JPEGXL_FORCE_SYSTEM_HWY"] = True
        tc.variables["JPEGXL_FORCE_SYSTEM_LCMS2"] = True
        tc.variables["JPEGXL_WARNINGS_AS_ERRORS"] = False
        tc.variables["JPEGXL_FORCE_NEON"] = False
        tc.variables["JPEGXL_ENABLE_AVX512"] = self.options.get_safe("avx512", False)
        tc.variables["JPEGXL_ENABLE_AVX512_SPR"] = self.options.get_safe("avx512_spr", False)
        tc.variables["JPEGXL_ENABLE_AVX512_ZEN4"] = self.options.get_safe("avx512_zen4", False)
        if cross_building(self):
            tc.variables["CMAKE_SYSTEM_PROCESSOR"] = str(self.settings.arch)
        # Allow non-cache_variables to be used
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0077"] = "NEW"
        # Skip the buggy custom FindAtomic and force the use of atomic library directly for libstdc++
        tc.variables["ATOMICS_LIBRARIES"] = "atomic" if self._atomic_required else ""
        if Version(self.version) >= "0.8":
            # TODO: add support for the jpegli JPEG encoder library
            tc.variables["JPEGXL_ENABLE_JPEGLI"] = False
            tc.variables["JPEGXL_ENABLE_JPEGLI_LIBJPEG"] = False
        # TODO: can hopefully be removed in newer versions
        # https://github.com/libjxl/libjxl/issues/3159
        if Version(self.version) >= "0.9" and self.settings.build_type == "Debug" and is_msvc(self):
            tc.preprocessor_definitions["JXL_DEBUG_V_LEVEL"] = 1
        tc.generate()

        deps = CMakeDeps(self)
        deps.set_property("brotli", "cmake_file_name", "Brotli")
        deps.set_property("highway", "cmake_file_name", "HWY")
        deps.set_property("lcms", "cmake_file_name", "LCMS2")
        deps.generate()

        # For tcmalloc
        deps = PkgConfigDeps(self)
        deps.generate()

    @property
    def _atomic_required(self):
        return self.settings.get_safe("compiler.libcxx") in ["libstdc++", "libstdc++11"]

    def _patch_sources(self):
        # Disable tools, extras and third_party
        save(self, os.path.join(self.source_folder, "tools", "CMakeLists.txt"), "")
        save(self, os.path.join(self.source_folder, "third_party", "CMakeLists.txt"), "")
        # FindAtomics.cmake values are set by CMakeToolchain instead
        save(self, os.path.join(self.source_folder, "cmake", "FindAtomics.cmake"), "")

        # Allow fPIC to be set by Conan
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"),
                        "set(CMAKE_POSITION_INDEPENDENT_CODE TRUE)", "")
        for cmake_file in ["jxl.cmake", "jxl_threads.cmake", "jxl_cms.cmake", "jpegli.cmake"]:
            path = os.path.join(self.source_folder, "lib", cmake_file)
            if os.path.exists(path):
                fpic = "ON" if self.options.get_safe("fPIC", True) else "OFF"
                replace_in_file(self, path, "POSITION_INDEPENDENT_CODE ON", f"POSITION_INDEPENDENT_CODE {fpic}")

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        if self.options.shared:
            rm(self, "*.a", os.path.join(self.package_folder, "lib"))
            rm(self, "*-static.lib", os.path.join(self.package_folder, "lib"))

    def _lib_name(self, name):
        if Version(self.version) < "0.9" and not self.options.shared and self.settings.os == "Windows":
            return name + "-static"
        return name

    def package_info(self):
        libcxx = stdcpp_library(self)

        # jxl
        self.cpp_info.components["jxl"].set_property("pkg_config_name", "libjxl")
        self.cpp_info.components["jxl"].libs = [self._lib_name("jxl")]
        self.cpp_info.components["jxl"].requires = ["brotli::brotli", "highway::highway", "lcms::lcms"]
        if self.options.with_tcmalloc:
            self.cpp_info.components["jxl"].requires.append("gperftools::tcmalloc_minimal")
        if self._atomic_required:
            self.cpp_info.components["jxl"].system_libs.append("atomic")
        if not self.options.shared:
            self.cpp_info.components["jxl"].defines.append("JXL_STATIC_DEFINE")
        if libcxx:
            self.cpp_info.components["jxl"].system_libs.append(libcxx)

        # jxl_cms
        if Version(self.version) >= "0.9.0":
            self.cpp_info.components["jxl_cms"].set_property("pkg_config_name", "libjxl_cms")
            self.cpp_info.components["jxl_cms"].libs = [self._lib_name("jxl_cms")]
            self.cpp_info.components["jxl_cms"].requires = ["lcms::lcms", "highway::highway"]
            if not self.options.shared:
                self.cpp_info.components["jxl"].defines.append("JXL_CMS_STATIC_DEFINE")
            if libcxx:
                self.cpp_info.components["jxl_cms"].system_libs.append(libcxx)

        # jxl_dec
        if Version(self.version) < "0.9.0":
            if not self.options.shared:
                self.cpp_info.components["jxl_dec"].set_property("pkg_config_name", "libjxl_dec")
                self.cpp_info.components["jxl_dec"].libs = [self._lib_name("jxl_dec")]
                self.cpp_info.components["jxl_dec"].requires = ["brotli::brotli", "highway::highway", "lcms::lcms"]
                if libcxx:
                    self.cpp_info.components["jxl_dec"].system_libs.append(libcxx)

        # jxl_threads
        self.cpp_info.components["jxl_threads"].set_property("pkg_config_name", "libjxl_threads")
        self.cpp_info.components["jxl_threads"].libs = [self._lib_name("jxl_threads")]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["jxl_threads"].system_libs = ["pthread"]
        if not self.options.shared:
            self.cpp_info.components["jxl_threads"].defines.append("JXL_THREADS_STATIC_DEFINE")
        if libcxx:
            self.cpp_info.components["jxl_threads"].system_libs.append(libcxx)
