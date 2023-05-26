from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, replace_in_file, rmdir

import os

required_conan_version = ">=1.54.0"


class Md4cConan(ConanFile):
    name = "md4c"
    description = "C Markdown parser. Fast. SAX-like interface. Compliant to CommonMark specification."
    license = "MIT"
    topics = ("markdown-parser", "markdown")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/mity/md4c"
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "encoding": ["utf-8", "utf-16", "ascii"],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "encoding": "utf-8",
    }

    def export_sources(self):
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

    def validate(self):
        if self.settings.os != "Windows" and self.options.encoding == "utf-16":
            raise ConanInvalidConfiguration(f"{self.ref} doesn't support utf-16 options on non-Windows platforms")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        if self.options.encoding == "utf-8":
            tc.preprocessor_definitions["MD4C_USE_UTF8"] = "1"
        elif self.options.encoding == "utf-16":
            tc.preprocessor_definitions["MD4C_USE_UTF16"] = "1"
        elif self.options.encoding == "ascii":
            tc.preprocessor_definitions["MD4C_USE_ASCII"] = "1"
        tc.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)
        # Honor encoding option
        replace_in_file(
            self,
            os.path.join(self.source_folder, "src", "CMakeLists.txt"),
            "COMPILE_FLAGS \"-DMD4C_USE_UTF8\"",
            "",
        )

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="LICENSE.md", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "md4c")

        self.cpp_info.components["_md4c"].set_property("cmake_target_name", "md4c::md4c")
        self.cpp_info.components["_md4c"].set_property("pkg_config_name", "md4c")
        self.cpp_info.components["_md4c"].libs = ["md4c"]
        if self.settings.os == "Windows" and self.options.encoding == "utf-16":
            self.cpp_info.components["_md4c"].defines.append("MD4C_USE_UTF16")

        self.cpp_info.components["md4c_html"].set_property("cmake_target_name", "md4c::md4c-html")
        self.cpp_info.components["md4c_html"].set_property("pkg_config_name", "md4c-html")
        self.cpp_info.components["md4c_html"].libs = ["md4c-html"]
        self.cpp_info.components["md4c_html"].requires = ["_md4c"]

        # workaround so that global target & pkgconfig file have all components while avoiding
        # to create unofficial target or pkgconfig file
        self.cpp_info.set_property("cmake_target_name", "md4c::md4c-html")
        self.cpp_info.set_property("pkg_config_name", "md4c-html")

        # TODO: to remove in conan v2
        self.cpp_info.components["_md4c"].names["cmake_find_package"] = "md4c"
        self.cpp_info.components["_md4c"].names["cmake_find_package_multi"] = "md4c"
        self.cpp_info.components["md4c_html"].names["cmake_find_package"] = "md4c-html"
        self.cpp_info.components["md4c_html"].names["cmake_find_package_multi"] = "md4c-html"
        self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))
