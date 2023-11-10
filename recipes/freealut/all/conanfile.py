from conan import ConanFile
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, export_conandata_patches, copy, get
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.61"

class FreeAlutConan(ConanFile):
    name = "freealut"
    description = "freealut is a free implementation of OpenAL's ALUT standard."
    topics = ("freealut", "openal", "audio", "api")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://directory.fsf.org/wiki/Freealut"
    license = "LGPL-2.0-or-later"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True
    }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.rm_safe("fPIC")

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
            self.options["openal-soft"].shared = True
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")
    
    def validate(self):
        if self.options.shared and \
           (not self.dependencies["openal-soft"].options.shared):
            raise ConanInvalidConfiguration(
                "If built as shared openal-soft must be shared as well. " 
                "Please, use `openal-soft/*:shared=True`.",
            )

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("openal-soft/1.22.2", transitive_headers=True, transitive_libs=True)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        apply_conandata_patches(self)

    def generate(self):
        tc = CMakeToolchain(self)
        # Honor BUILD_SHARED_LIBS from conan_toolchain (see https://github.com/conan-io/conan/issues/11840)
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0077"] = "NEW"
        tc.cache_variables["BUILD_SHARED_LIBS"] = self.options.shared
        tc.generate()
        CMakeDeps(self).generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ['alut']
        self.cpp_info.includedirs.append(os.path.join("include", "AL"))
        if(not self.options.shared):
            self.cpp_info.defines.append("ALUT_LIBTYPE_STATIC")
