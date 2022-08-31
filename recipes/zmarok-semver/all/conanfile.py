from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import apply_conandata_patches, copy, get
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
import os


required_conan_version = ">=1.50.0"


class ZmarokSemverConan(ConanFile):
    name = "zmarok-semver"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/zmarko/semver"
    description = "Semantic versioning for cpp14"
    topics = ("versioning", "semver", "semantic")
    settings = "os", "compiler", "arch", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def export_sources(self):
        for p in self.conan_data.get("patches", {}).get(self.version, []):
            copy(self, p["patch_file"], self.recipe_folder, self.export_sources_folder)

    def validate(self):
        if self.info.settings.os == "Windows" and self.info.options.shared:
            raise ConanInvalidConfiguration("Shared library on Windows is not supported.")
        if self.info.settings.compiler.cppstd:
            check_min_cppstd(self, 14)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True, destination=self.source_folder)

    def layout(self):
        cmake_layout(self, src_folder="src")

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

    def package_info(self):
        self.cpp_info.libs = ["semver"]
