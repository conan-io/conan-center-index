import os

from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, collect_libs, copy, export_conandata_patches, get
from conan.tools.microsoft import is_msvc

required_conan_version = ">=2.1"


class LibBasisUniversalConan(ConanFile):
    name = "libbasisu"
    description = "Basis Universal Supercompressed GPU Texture Codec"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/BinomialLLC/basis_universal"
    topics = ("basis", "textures", "compression")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "use_sse4": [True, False],
        "with_zstd": [True, False],
        "enable_encoder": [True, False],
        "custom_iterator_debug_level": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "use_sse4": False,
        "with_zstd": True,
        "enable_encoder": True,
        "custom_iterator_debug_level": False,
    }

    def _use_custom_iterator_debug_level(self):
        return self.options.get_safe("custom_iterator_debug_level",
                                     default=self.default_options["custom_iterator_debug_level"])

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if not is_msvc(self):
            self.options.rm_safe("custom_iterator_debug_level")

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def requirements(self):
        if self.options.with_zstd:
            self.requires("zstd/[>=1.5.5 <2]")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def validate(self):
        check_min_cppstd(self, 11)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        apply_conandata_patches(self)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["SSE4"] = self.options.use_sse4
        tc.cache_variables["ZSTD"] = self.options.with_zstd
        tc.cache_variables["ENABLE_ENCODER"] = self.options.enable_encoder
        tc.cache_variables["NO_ITERATOR_DEBUG_LEVEL"] = not self._use_custom_iterator_debug_level()
        tc.generate()
        tc = CMakeDeps(self)
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE",
             dst=os.path.join(self.package_folder, "licenses"),
             src=self.source_folder)
        copy(self, "*.h",
            dst=os.path.join(self.package_folder, "include", self.name, "transcoder"),
            src=os.path.join(self.source_folder, "transcoder"))
        if self.options.enable_encoder:
            copy(self,"*.h",
                dst=os.path.join(self.package_folder, "include", self.name, "encoder"),
                src=os.path.join(self.source_folder, "encoder"))
        for pattern in ["*.a", "*.so*", "*.dylib*", "*.lib"]:
            copy(self, pattern,
                 dst=os.path.join(self.package_folder, "lib"),
                 src=self.build_folder, keep_path=False)
        copy(self, "*.dll",
             dst=os.path.join(self.package_folder, "bin"),
             src=self.build_folder, keep_path=False)

    def package_info(self):
        self.cpp_info.libs = collect_libs(self)
        self.cpp_info.includedirs = ["include", os.path.join("include", self.name)]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["m", "pthread"]
        self.cpp_info.defines.append(
            "BASISU_NO_ITERATOR_DEBUG_LEVEL={}".format("1" if self._use_custom_iterator_debug_level() else "0")
        )
