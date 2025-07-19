from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, export_conandata_patches, apply_conandata_patches, rm, rmdir
from conan.tools.microsoft import is_msvc, is_msvc_static_runtime
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=2.0.9"

class DsS3UploaderConan(ConanFile):
    name = "ds_s3_uploader"
    version = "1.0.0"
    description = "An S3 uploader library for Every ObjectStorage System"
    license = "MIT"
    url = "https://github.com/mhr05121384/ds_s3_uploader"
    homepage = "https://github.com/mhr05121384/ds_s3_uploader"
    topics = ("s3", "uploader", "arvan", "aws")
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

    def export_sources(self):
        export_conandata_patches(self)
        copy(self, "CMakeLists.txt", self.recipe_folder, self.export_sources_folder)
        copy(self, "src/*", self.recipe_folder, os.path.join(self.export_sources_folder, "src"))
        copy(self, "include/*", self.recipe_folder, os.path.join(self.export_sources_folder, "include"))

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        requirements = self.conan_data.get("requirements", [])
        for r in requirements:
            self.requires(r)

    def validate(self):
        check_min_cppstd(self, 17)
        if is_msvc(self) and self.options.shared:
            raise ConanInvalidConfiguration(f"{self.ref} cannot be built as shared with MSVC.")

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.16 <4]")

    def source(self):
        apply_conandata_patches(self)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["DS_S3_UPLOADER_BUILD_TESTS"] = False
        if is_msvc(self):
            tc.cache_variables["USE_MSVC_RUNTIME_LIBRARY_DLL"] = not is_msvc_static_runtime(self)
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

        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        rm(self, "*.pdb", self.package_folder, recursive=True)

    def package_info(self):
        self.cpp_info.libs = ["ds_s3_uploader"]
        self.cpp_info.includedirs = ["include"]

        self.cpp_info.set_property("cmake_file_name", "ds_s3_uploader")
        self.cpp_info.set_property("cmake_target_name", "ds_s3_uploader::ds_s3_uploader")
        self.cpp_info.set_property("pkg_config_name", "ds_s3_uploader")

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["m", "pthread", "dl"])
