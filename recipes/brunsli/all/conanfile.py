import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get, copy, replace_in_file, save

required_conan_version = ">=1.53.0"

class PackageConan(ConanFile):
    name = "brunsli"
    description = "Practical JPEG Repacker"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/google/brunsli"
    topics = ("jpeg", "repacker", "codec", "brotli", "wasm")

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

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.options["brotli"].shared = False

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("brotli/1.0.9", transitive_libs=True)

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, 11)
        if self.dependencies["brotli"].options.shared:
            raise ConanInvalidConfiguration("brotli must be built as a static library")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["BUILD_TESTING"] = False
        # TODO: add WASM support
        tc.cache_variables["BRUNSLI_EMSCRIPTEN"] = False
        tc.variables["CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS"] = True
        tc.generate()

        deps = CMakeDeps(self)
        deps.set_property("brotli::brotlidec", "cmake_target_name", "brotlidec-static")
        deps.set_property("brotli::brotlienc", "cmake_target_name", "brotlienc-static")
        deps.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)
        # Allow Conan to control the linkage type of the output libraries
        if not self.options.shared:
            replace_in_file(self, os.path.join(self.source_folder, "brunsli.cmake"), " SHARED", "")
            save(self, os.path.join(self.source_folder, "brunsli.cmake"),
                 "\ninstall(TARGETS brunslicommon-static brunslidec-static brunslienc-static)",
                 append=True)
        # Fix DLL installation
        replace_in_file(self, os.path.join(self.source_folder, "brunsli.cmake"),
                        'LIBRARY DESTINATION "${CMAKE_INSTALL_LIBDIR}"',
                        'LIBRARY DESTINATION "${CMAKE_INSTALL_LIBDIR}" '
                        'RUNTIME DESTINATION "${CMAKE_INSTALL_BINDIR}"')

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.components["brunslidec-c"].libs = ["brunslidec-c"]
        self.cpp_info.components["brunslienc-c"].libs = ["brunslienc-c"]
        if not self.options.shared:
            self.cpp_info.components["brunslidec-c"].libs += ["brunslicommon-static", "brunslidec-static"]
            self.cpp_info.components["brunslienc-c"].libs += ["brunslicommon-static", "brunslienc-static"]
