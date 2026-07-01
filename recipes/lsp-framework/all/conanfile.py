from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, move_folder_contents, rm, rmdir
from conan.tools.microsoft import is_msvc, is_msvc_static_runtime
import os


required_conan_version = ">=2.0.9"


class PackageConan(ConanFile):
    name = "lsp-framework"
    description = "Language Server Protocol implementation in C++"
    license = "MIT"
    url = "https://github.com/leon-bckl/lsp-framework"
    homepage = "https://github.com/leon-bckl/lsp-framework"
    topics = ("language-server-protocol", "lsp", "lsp-server", "lsp-client")
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

    def layout(self):
        cmake_layout(self, src_folder="src")

    def validate(self):
        check_min_cppstd(self, 20)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        apply_conandata_patches(self)

    def generate(self):
        tc = CMakeToolchain(self)
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

        # fix install weirdness: for whatever reason, when Conan generates this, it seems to embed an "LSP"
        # directory that is one level too deep, so we fix that here
        copy(self, pattern="**", src=os.path.join(self.package_folder, "include", "lsp", "lsp"),
            dst=os.path.join(self.package_folder, "include", "lsp"))
        rmdir(self, os.path.join(self.package_folder, "include", "lsp", "lsp"))

        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        rm(self, "*.pdb", self.package_folder, recursive=True)

    def package_info(self):
        self.cpp_info.libs = ["lsp"]
        self.cpp_info.set_property("cmake_file_name", "lsp")
        self.cpp_info.set_property("cmake_target_name", "lsp::lsp")

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")
            self.cpp_info.system_libs.append("pthread")
            self.cpp_info.system_libs.append("dl")
