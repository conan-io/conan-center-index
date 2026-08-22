from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get
import os


required_conan_version = ">=1.53.0"


class ZmarokSemverConan(ConanFile):
    name = "zmarok-semver"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/zmarko/semver"
    description = "Semantic versioning for cpp14"
    topics = ("versioning", "semver", "semantic")
    package_type = "library"
    settings = "os", "compiler", "arch", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False]
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

    def layout(self):
        cmake_layout(self, src_folder="src")

    def validate(self):
        if self.settings.os == "Windows" and self.options.shared:
            raise ConanInvalidConfiguration("Shared library on Windows is not supported.")
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, 14)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        gt = CMakeToolchain(self)
        gt.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        # Parent Build system does not support installation; so we must manually package
        hdr_src = os.path.join(self.source_folder, "include")
        hdr_dst = os.path.join(self.package_folder, "include")
        copy(self, "*.h", hdr_src, hdr_dst)
        copy(self, "*.inl", hdr_src, hdr_dst)

        lib_dir = os.path.join(self.package_folder, "lib")
        copy(self, "*.a", self.build_folder, lib_dir, keep_path=False)
        copy(self, "*.lib", self.build_folder, lib_dir, keep_path=False)
        copy(self, "*.so", self.build_folder, lib_dir, keep_path=False)
        copy(self, "*.dylib", self.build_folder, lib_dir, keep_path=False)
        copy(self, "*.dll*", self.build_folder, os.path.join(self.package_folder, "bin"), keep_path=False)
        fix_apple_shared_install_name(self)

    def package_info(self):
        self.cpp_info.libs = ["semver"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["m"]
