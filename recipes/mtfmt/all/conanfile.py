from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rm, rmdir
from conan.tools.microsoft import is_msvc
import os


required_conan_version = ">=1.53.0"


class MtFmtConan(ConanFile):
    name = "mtfmt"
    description = "mtfmt (Mini template formatter) is a formatting library designed for embedded systems"
    license = "LGPL-3.0-only"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/MtFmT-Lib/mtfmt"
    topics = ("formatting", "embedded")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "use_div": [True, False],
        "use_malloc": [True, False],
        "use_stdout": [True, False],
        "use_assert": [True, False],
        "use_utf8": [True, False],
        "use_fp32": [True, False],
        "use_fp64": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "use_div": False,
        "use_malloc": False,
        "use_stdout": False,
        "use_assert": False,
        "use_utf8": True,
        "use_fp32": False,
        "use_fp64": False,
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def validate(self):
        # Windows always builds as release, debug is not supported
        if is_msvc(self) and self.settings.build_type == "Debug":
            raise ConanInvalidConfiguration(f"{self.ref} does not support MSVC debug builds")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["MTFMT_BUILD_SHARED"] = self.options.shared
        tc.cache_variables["MTFMT_RT_USE_DIV"] = self.options.use_div
        tc.cache_variables["MTFMT_RT_USE_MALLOC"] = self.options.use_malloc
        tc.cache_variables["MTFMT_RT_USE_STDOUT"] = self.options.use_stdout
        tc.cache_variables["MTFMT_RT_USE_ASSERT"] = self.options.use_assert
        tc.cache_variables["MTFMT_RT_USE_UTF8"] = self.options.use_utf8
        tc.cache_variables["MTFMT_RT_USE_FP32"] = self.options.use_fp32
        tc.cache_variables["MTFMT_RT_USE_FP64"] = self.options.use_fp64
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0077"] = "NEW"
        tc.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "mtfmt", "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "mtfmt", "share"))
        rm(self, "*.la", os.path.join(self.package_folder, "mtfmt", "lib"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "mtfmt", "lib"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "mtfmt", "bin"))

    def package_info(self):
        suffix = "_d" if self.settings.build_type == "Debug" else ""
        self.cpp_info.libs = ["mtfmt" + suffix]

        libdir = os.path.join("mtfmt", "lib")

        if not self.options.shared or self.settings.os == "Windows":
            libdir = os.path.join(libdir, "static")

        self.cpp_info.libdirs = [libdir]
        self.cpp_info.includedirs = [os.path.join("mtfmt", "include")]
        self.cpp_info.bindirs = [os.path.join("mtfmt", "bin")]
