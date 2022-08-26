from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, get, rmdir
import os

required_conan_version = ">=1.50.0"


class BrotliConan(ConanFile):
    name = "brotli"
    description = "Brotli compression format"
    topics = ("brotli", "compression")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/google/brotli"
    license = "MIT",

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "target_bits": [64, 32, None],
        "endianness": ["big", "little", "neutral", None],
        "enable_portable": [True, False],
        "enable_rbit": [True, False],
        "enable_debug": [True, False],
        "enable_log": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "target_bits": None,
        "endianness": None,
        "enable_portable": False,
        "enable_rbit": True,
        "enable_debug": False,
        "enable_log": False,
    }

    def export_sources(self):
        for p in self.conan_data.get("patches", {}).get(self.version, []):
            copy(self, p["patch_file"], self.recipe_folder, self.export_sources_folder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        try:
            del self.settings.compiler.libcxx
        except Exception:
            pass
        try:
            del self.settings.compiler.cppstd
        except Exception:
            pass

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BROTLI_BUNDLED_MODE"] = False
        tc.variables["BROTLI_DISABLE_TESTS"] = True
        if self.options.get_safe("target_bits") == 32:
            tc.preprocessor_definitions["BROTLI_BUILD_32_BIT"] = 1
        elif self.options.get_safe("target_bits") == 64:
            tc.preprocessor_definitions["BROTLI_BUILD_64_BIT"] = 1
        if self.options.get_safe("endianness") == "big":
            tc.preprocessor_definitions["BROTLI_BUILD_BIG_ENDIAN"] = 1
        elif self.options.get_safe("endianness") == "neutral":
            tc.preprocessor_definitions["BROTLI_BUILD_ENDIAN_NEUTRAL"] = 1
        elif self.options.get_safe("endianness") == "little":
            tc.preprocessor_definitions["BROTLI_BUILD_LITTLE_ENDIAN"] = 1
        if self.options.enable_portable:
            tc.preprocessor_definitions["BROTLI_BUILD_PORTABLE"] = 1
        if not(self.options.enable_rbit):
            tc.preprocessor_definitions["BROTLI_BUILD_NO_RBIT"] = 1
        if self.options.enable_debug:
            tc.preprocessor_definitions["BROTLI_DEBUG"] = 1
        if self.options.enable_log:
            tc.preprocessor_definitions["BROTLI_ENABLE_LOG"] = 1
        # To install relocatable shared libs on Macos
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0042"] = "NEW"
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        includedir = os.path.join("include", "brotli")
        # brotlicommon
        self.cpp_info.components["brotlicommon"].set_property("pkg_config_name", "libbrotlicommon")
        self.cpp_info.components["brotlicommon"].includedirs.append(includedir)
        self.cpp_info.components["brotlicommon"].libs = [self._get_decorated_lib("brotlicommon")]
        if self.settings.os == "Windows" and self.options.shared:
            self.cpp_info.components["brotlicommon"].defines.append("BROTLI_SHARED_COMPILATION")
        # brotlidec
        self.cpp_info.components["brotlidec"].set_property("pkg_config_name", "libbrotlidec")
        self.cpp_info.components["brotlidec"].includedirs.append(includedir)
        self.cpp_info.components["brotlidec"].libs = [self._get_decorated_lib("brotlidec")]
        self.cpp_info.components["brotlidec"].requires = ["brotlicommon"]
        # brotlienc
        self.cpp_info.components["brotlienc"].set_property("pkg_config_name", "libbrotlienc")
        self.cpp_info.components["brotlienc"].includedirs.append(includedir)
        self.cpp_info.components["brotlienc"].libs = [self._get_decorated_lib("brotlienc")]
        self.cpp_info.components["brotlienc"].requires = ["brotlicommon"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["brotlienc"].system_libs = ["m"]

        # TODO: to remove in conan v2 once cmake_find_package* & pkg_config generators removed.
        #       do not set this target in CMakeDeps, it was a mistake, there is no official brotil config file, nor Find module file
        self.cpp_info.names["cmake_find_package"] = "Brotli"
        self.cpp_info.names["cmake_find_package_multi"] = "Brotli"
        self.cpp_info.components["brotlicommon"].names["pkg_config"] = "libbrotlicommon"
        self.cpp_info.components["brotlidec"].names["pkg_config"] = "libbrotlidec"
        self.cpp_info.components["brotlienc"].names["pkg_config"] = "libbrotlienc"

    def _get_decorated_lib(self, name):
        libname = name
        if not self.options.shared:
            libname += "-static"
        return libname
