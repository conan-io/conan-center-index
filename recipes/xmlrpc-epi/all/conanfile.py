import os

from conan import ConanFile
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, export_conandata_patches, copy, get, replace_in_file


required_conan_version = ">=1.53.0"


class XMLRPCEPIRecipe(ConanFile):
    name = "xmlrpc-epi"
    description = "An implementation of the xmlrpc protocol in C"
    license = "MIT"
    homepage = "https://xmlrpc-epi.sourceforge.net/"
    url = "https://github.com/conan-io/conan-center-index"
    topics = ("xml-rpc", "http")
    package_type = "library"

    # Binary configuration
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    def requirements(self):
        self.requires("expat/2.5.0")
        if self.settings.os in ("Windows", "Macos"):
            self.requires("libiconv/1.17")

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.rm_safe("fPIC")

    def configure(self):
        # This is a c-only library, remove C++ compiler settings
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def export_sources(self):
        export_conandata_patches(self)
        copy(self, "CMakeLists.txt",
             src=self.recipe_folder,
             dst=os.path.join(self.export_sources_folder, "src"))

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def generate(self):
        tc = CMakeToolchain(self)
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)
        if self.settings.build_type == "Debug":
            # Remove inlines from source files so that we can link the debug build
            replace_in_file(self, os.path.join(self.source_folder, "src/xml_to_soap.c"), "inline", "")
            replace_in_file(self, os.path.join(self.source_folder, "src/xmlrpc_introspection.c"), "inline", "")

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="COPYING", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        copy(self, pattern="AUTHORS", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["xmlrpc-epi"]
