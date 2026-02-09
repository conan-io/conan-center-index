from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os
from conan.tools.build import check_min_cppstd, stdcpp_library, cross_building, check_max_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rmdir, save, replace_in_file
from conan.tools.scm import Version
import os

required_conan_version = ">=2"


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
        self.requires("zstd/[^1.5]")
        if self.options.tools:
            self.requires("fmt/[>=11 <12]")

    def validate_build(self):
        if self.options.tools:
            if cross_building(self) and is_apple_os(self):
                raise ConanInvalidConfiguration(f"Cross-building KTX tools {self.version} for Apple OS is not supported in this version")
            # Does not compile with newer cppstd versions.
            check_max_cppstd(self, 17)

    def validate(self):
        check_min_cppstd(self, 17)
        if self.settings.compiler == "gcc" and Version(self.settings.compiler.version) < 6:
            # astcenc_vecmathlib_sse_4.h:809:41: error: the last argument must be a 4-bit immediate
            raise ConanInvalidConfiguration("GCC v6+ is required")

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.22]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        # Disable tests (and avoid copying them, it's a large folder)
        rmdir(self, os.path.join(self.source_folder, "tests"))
        save(self, os.path.join(self.source_folder, "tests", "CMakeLists.txt"), "")
        replace_in_file(self, os.path.join(self.source_folder, "external", "astc-encoder", "CMakeLists.txt"),
                        "set(CMAKE_CXX_STANDARD", "#")
        apply_conandata_patches(self)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["KTX_FEATURE_TOOLS"] = self.options.tools
        tc.variables["KTX_FEATURE_DOC"] = False
        tc.variables["KTX_FEATURE_LOADTEST_APPS"] = False
        tc.variables["KTX_FEATURE_TESTS"] = False
        tc.variables["BASISU_SUPPORT_SSE"] = self.options.get_safe("sse", False)
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
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

        self.cpp_info.components["libktx"].set_property("cmake_target_name", "KTX::ktx")
        self.cpp_info.components["libktx"].requires = ["zstd::zstd"]
        if self.options.tools:
            self.cpp_info.components["libktx"].requires.append("fmt::fmt")
