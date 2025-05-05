from conan import ConanFile
from conan.tools.build import check_min_cppstd, stdcpp_library
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rmdir
import os

required_conan_version = ">=1.53.0"


class KtxConan(ConanFile):
    name = "ktx"
    description = "Khronos Texture library and tool."
    license = "Apache-2.0"
    topics = ("texture", "khronos")
    homepage = "https://github.com/KhronosGroup/KTX-Software"
    url = "https://github.com/conan-io/conan-center-index"
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "sse": [True, False],
        "tools": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "sse": True,
        "tools": True,
    }

    @property
    def _has_sse_support(self):
        return self.settings.arch in ["x86", "x86_64"]

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if not self._has_sse_support:
            del self.options.sse
        if self.settings.os in ["iOS", "Android", "Emscripten"]:
            # tools are not build by default if iOS, Android or Emscripten
            self.options.tools = False

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("lodepng/cci.20230410")
        self.requires("zstd/1.5.5")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, 11)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["KTX_FEATURE_TOOLS"] = self.options.tools
        tc.variables["KTX_FEATURE_DOC"] = False
        tc.variables["KTX_FEATURE_LOADTEST_APPS"] = False
        tc.variables["KTX_FEATURE_STATIC_LIBRARY"] = not self.options.shared
        tc.variables["KTX_FEATURE_TESTS"] = False
        tc.variables["BASISU_SUPPORT_SSE"] = self.options.get_safe("sse", False)
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)
        # Unvendor several libs (we rely on patch files to link those libs)
        # It's worth noting that vendored jpeg-compressor can't be replaced by CCI equivalent
        basisu_dir = os.path.join(self.source_folder, "lib", "basisu")
        ## lodepng (the patch file 0002-lodepng-no-export-symbols is important, in order to not try to export lodepng symbols)
        os.remove(os.path.join(basisu_dir, "encoder", "lodepng.cpp"))
        os.remove(os.path.join(basisu_dir, "encoder", "lodepng.h"))
        ## zstd
        rmdir(self, os.path.join(basisu_dir, "zstd"))

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE.md", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "*", src=os.path.join(self.source_folder, "LICENSES"), dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "Ktx")
        self.cpp_info.set_property("cmake_target_name", "KTX::ktx")
        # TODO: back to root level in conan v2
        self.cpp_info.components["libktx"].libs = ["ktx"]
        self.cpp_info.components["libktx"].defines = [
            "KTX_FEATURE_KTX1", "KTX_FEATURE_KTX2", "KTX_FEATURE_WRITE"
        ]
        if not self.options.shared:
            self.cpp_info.components["libktx"].defines.append("KHRONOS_STATIC")
            libcxx = stdcpp_library(self)
            if libcxx:
                self.cpp_info.components["libktx"].system_libs.append(libcxx)
        if self.settings.os == "Windows":
            self.cpp_info.components["libktx"].defines.append("BASISU_NO_ITERATOR_DEBUG_LEVEL")
        elif self.settings.os == "Linux":
            self.cpp_info.components["libktx"].system_libs.extend(["m", "dl", "pthread"])

        # TODO: to remove in conan v2
        self.cpp_info.filenames["cmake_find_package"] = "Ktx"
        self.cpp_info.filenames["cmake_find_package_multi"] = "Ktx"
        self.cpp_info.names["cmake_find_package"] = "KTX"
        self.cpp_info.names["cmake_find_package_multi"] = "KTX"
        self.cpp_info.components["libktx"].names["cmake_find_package"] = "ktx"
        self.cpp_info.components["libktx"].names["cmake_find_package_multi"] = "ktx"
        self.cpp_info.components["libktx"].set_property("cmake_target_name", "KTX::ktx")
        self.cpp_info.components["libktx"].requires = ["lodepng::lodepng", "zstd::zstd"]
        if self.options.tools:
            self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))
