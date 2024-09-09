import os

from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, export_conandata_patches, get, load, replace_in_file, save, rename

required_conan_version = ">=1.53.0"


class CgltfConan(ConanFile):
    name = "cgltf"
    description = "Single-file glTF 2.0 loader and writer written in C99."
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/jkuhlmann/cgltf"
    topics = ("gltf", "header-only")

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

    def export_sources(self):
        copy(self, "CMakeLists.txt", src=self.recipe_folder, dst=self.export_sources_folder)
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def _create_source_files(self):
        cgltf_c = '#define CGLTF_IMPLEMENTATION\n#include "cgltf.h"\n'
        cgltf_write_c = '#define CGLTF_WRITE_IMPLEMENTATION\n#include "cgltf_write.h"\n'
        save(self, os.path.join(self.build_folder, self.source_folder, "cgltf.c"), cgltf_c)
        save(self, os.path.join(self.build_folder, self.source_folder, "cgltf_write.c"), cgltf_write_c)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.generate()

    def build(self):
        self._create_source_files()
        cmake = CMake(self)
        cmake.configure(build_script_folder=self.source_path.parent)
        cmake.build()

    def _remove_implementation(self, header_fullpath):
        header_content = load(self, header_fullpath)
        begin = header_content.find("/*\n *\n * Stop now, if you are only interested in the API.")
        end = header_content.find("/* cgltf is distributed under MIT license:", begin)
        implementation = header_content[begin:end]
        replace_in_file(
            self,
            header_fullpath,
            implementation,
            "/**\n * Implementation removed by conan during packaging.\n * Don't forget to link libs provided in this package.\n */\n\n",
        )

    def package(self):
        copy(self, "LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()
        for header_file in ["cgltf.h", "cgltf_write.h"]:
            header_fullpath = os.path.join(self.package_folder, "include", header_file)
            self._remove_implementation(header_fullpath)
        for dll in (self.package_path / "lib").glob("*.dll"):
            rename(self, dll, self.package_path / "bin" / dll.name)

    def package_info(self):
        self.cpp_info.libs = ["cgltf"]
