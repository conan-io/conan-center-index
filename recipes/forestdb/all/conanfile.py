import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get

required_conan_version = ">=1.53.0"


class ForestDBConan(ConanFile):
    name = "forestdb"
    description = "ForestDB is a KeyValue store based on a Hierarchical B+-Tree."
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/ForestDB-KVStore/forestdb"
    topics = ("kv-store", "mvcc", "wal")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_snappy": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_snappy": False,
    }

    def export_sources(self):
        export_conandata_patches(self)

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if self.options.with_snappy:
            self.requires("snappy/1.1.10")

    def validate(self):
        if self.settings.os == "Windows":
            raise ConanInvalidConfiguration("Windows Builds Unsupported")
        if self.settings.compiler == "clang":
            if self.settings.compiler.libcxx == "libc++" and not self.options.shared:
                raise ConanInvalidConfiguration("LibC++ Static Builds Unsupported")
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, 11)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["SNAPPY_OPTION"] = "Disable"
        if self.options.with_snappy:
            tc.variables["SNAPPY_OPTION"] = "Enable"
        tc.generate()
        tc = CMakeDeps(self)
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        lib_target = "forestdb"
        if not self.options.shared:
            lib_target = "static_lib"
        cmake = CMake(self)
        cmake.configure()
        cmake.build(target=lib_target)

    def package(self):
        copy(self, "LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        # Parent Build system does not support library type selection
        # and will only install the shared object from cmake; so we must
        # handpick our libraries.
        for pattern in ["*.a*", "*.lib", "*.so*", "*.dylib*", "*.dll*"]:
            copy(self, pattern,
                 dst=os.path.join(self.package_folder, "lib"),
                 src=self.build_folder)
        copy(self, "*.h",
             dst=os.path.join(self.package_folder, "include"),
             src=os.path.join(self.source_folder, "include"),
             keep_path=True)

    def package_info(self):
        self.cpp_info.libs = ["forestdb"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["pthread", "m", "dl", "rt"]
