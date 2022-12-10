from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, load, replace_in_file
import os
import shutil

required_conan_version = ">=1.53.0"


class JsmnConan(ConanFile):
    name = "jsmn"
    description = (
        "jsmn (pronounced like 'jasmine') is a minimalistic JSON parser in C. "
        "It can be easily integrated into resource-limited or embedded projects."
    )
    license = "MIT"
    topics = ("json", "parser")
    homepage = "https://github.com/zserge/jsmn"
    url = "https://github.com/conan-io/conan-center-index"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_parent_links": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_parent_links": False,
    }

    def export_sources(self):
        copy(self, "CMakeLists.txt", self.recipe_folder, self.export_sources_folder)
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["JSMN_SRC_DIR"] = self.source_folder.replace("\\", "/")
        tc.variables["JSMN_PARENT_LINKS"] = self.options.with_parent_links
        tc.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)
        # Split in jsmn.h & jsmn.c
        jsmn_header = os.path.join(self.source_folder, "jsmn.h")
        shutil.copy(jsmn_header, os.path.join(self.source_folder, "jsmn.c"))
        # Remove implementation from jsmn.h
        header_content = load(self, jsmn_header)
        begin = header_content.find("#ifndef JSMN_HEADER")
        endPattern = "#endif /* JSMN_HEADER */"
        end = header_content.find(endPattern, begin) + len(endPattern)
        implementation = header_content[begin:end]
        replace_in_file(self, jsmn_header, implementation, "")

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure(build_script_folder=os.path.join(self.source_folder, os.pardir))
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["jsmn"]
        if self.options.with_parent_links:
            self.cpp_info.defines.append("JSMN_PARENT_LINKS")
