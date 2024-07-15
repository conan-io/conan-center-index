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
        "use_stdout": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "use_stdout": False,
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        # for plain C projects only
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        # src_folder must use the same source folder name the project
        cmake_layout(self, src_folder="src")

    def validate(self):
        # Windows always builds as release, debug is not supported
        if is_msvc(self):
            raise ConanInvalidConfiguration(f"{self.ref} does not support MSVC debug builds")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["MTFMT_BUILD_SHARED"] = self.options.shared
        tc.variables["MTFMT_RT_USE_STDOUT"] = self.options.use_stdout
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

        # some files extensions and folders are not allowed. Please, read the FAQs to get informed.
        rmdir(self, os.path.join(self.package_folder, "mtfmt", "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        rm(self, "*.la", os.path.join(self.package_folder, "mtfmt", "lib"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "mtfmt", "lib"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "mtfmt", "bin"))

    def package_info(self):
        suffix = "_d" if self.settings.build_type == "Debug" else ""
        self.cpp_info.libs = ["mtfmt" + suffix]
        self.cpp_info.libdirs = [os.path.join("mtfmt", "lib") if self.options.shared else os.path.join("mtfmt", "lib", "static")]
        self.cpp_info.bindirs = [os.path.join("mtfmt", "bin")]
        self.cpp_info.includedirs = [os.path.join("mtfmt", "include")]
        if self.options.use_stdout:
            self.cpp_info.defines = ["_MSTR_USE_STD_IO"]
