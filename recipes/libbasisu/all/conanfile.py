import os

from conan import ConanFile
from conan.tools.build import check_min_cppstd, valid_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version

required_conan_version = ">=2.0"


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
        "enable_encoder": [True, False],
        "custom_iterator_debug_level": [True, False],
        "with_zstd": [True, False],
        "with_opencl": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "use_sse4": False,
        "enable_encoder": True,
        "custom_iterator_debug_level": False,
        "with_zstd": True,
        "with_opencl": True,
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
        if Version(self.version) < "1.16":
            del self.options.with_opencl

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def requirements(self):
        if self.options.with_zstd:
            self.requires("zstd/1.5.5")
        if self.options.get_safe("with_opencl"):
            self.requires("opencl-icd-loader/2023.12.14")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def validate(self):
        check_min_cppstd(self, 11)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        apply_conandata_patches(self)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["SSE4"] = self.options.use_sse4
        tc.variables["ZSTD"] = self.options.with_zstd
        tc.variables["WITH_OPENCL"] = self.options.get_safe("with_opencl", False)
        tc.variables["ENABLE_ENCODER"] = self.options.enable_encoder
        tc.variables["NO_ITERATOR_DEBUG_LEVEL"] = not self._use_custom_iterator_debug_level()
        tc.variables["CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS"] = True
        if not valid_min_cppstd(self, self._min_cppstd):
            tc.variables["CMAKE_CXX_STANDARD"] = self._min_cppstd
        tc.generate()

        deps = CMakeDeps(self)
        deps.set_property("zstd", "cmake_target_name", "zstd::libzstd")
        deps.set_property("opencl-icd-loader", "cmake_file_name", "OpenCL")
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        copy(self, "*.h",
             src=os.path.join(self.source_folder, "transcoder"),
             dst=os.path.join(self.package_folder, "include", self.name, "transcoder"))
        if self.options.enable_encoder:
            copy(self,"*.h",
                 src=os.path.join(self.source_folder, "encoder"),
                 dst=os.path.join(self.package_folder, "include", self.name, "encoder"))

    def package_info(self):
        self.cpp_info.libs = ["basisu"]
        self.cpp_info.includedirs = ["include", os.path.join("include", self.name)]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["m", "pthread"]
        self.cpp_info.defines.append(
            "BASISU_NO_ITERATOR_DEBUG_LEVEL={}".format("1" if self._use_custom_iterator_debug_level() else "0")
        )
