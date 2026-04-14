from conan import ConanFile
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rmdir
import os


required_conan_version = ">=2.4"

# mirror
class ZydisConan(ConanFile):
    name = "zydis"
    description = "Fast and lightweight x86/x86-64 disassembler and code generation library"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://zydis.re"
    topics = ("x86-64", "disassembler", "codegen")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }
    implements = ["auto_shared_fpic"]
    languages = "C"

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        apply_conandata_patches(self)

    def requirements(self):
        self.requires("zycore/1.5.2", transitive_headers=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["ZYDIS_BUILD_SHARED_LIB"] = self.options.shared
        tc.cache_variables["ZYAN_SYSTEM_ZYCORE"] = True
        tc.cache_variables["ZYDIS_BUILD_EXAMPLES"] = False
        tc.cache_variables["ZYDIS_BUILD_TOOLS"] = False
        tc.cache_variables["ZYDIS_BUILD_DOXYGEN"] = False
        tc.cache_variables["ZYDIS_BUILD_TESTS"] = False
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.libs = ["Zydis"]
        self.cpp_info.set_property("cmake_file_name", "Zydis")
        self.cpp_info.set_property("cmake_target_name", "Zydis::Zydis")

        if not self.options.shared:
            self.cpp_info.defines = ["ZYDIS_STATIC_BUILD"]
