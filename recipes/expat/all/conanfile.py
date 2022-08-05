from conan import ConanFile, tools
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, collect_libs, copy, rmdir
from conan.tools.microsoft import is_msvc, is_msvc_static_runtime
from conan.tools.scm import Version
import os

required_conan_version = ">=1.50.0"


class ExpatConan(ConanFile):
    name = "expat"
    description = "Fast streaming XML parser written in C."
    topics = ("expat", "xml", "parsing")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/libexpat/libexpat"
    license = "MIT"
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "char_type": ["char", "wchar_t", "ushort"],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "char_type": "char",
    }

    def export_sources(self):
        for p in self.conan_data.get("patches", {}).get(self.version, []):
            copy(self, p["patch_file"], self.recipe_folder, self.export_sources_folder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if Version(self.version) < "2.2.8":
            del self.options.char_type

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        tools.files.get(self,
            **self.conan_data["sources"][self.version],
            destination=self.source_folder,
            strip_root=True
        )

    def generate(self):
        tc = CMakeToolchain(self)
        if Version(self.version) < "2.2.8":
            tc.variables["BUILD_doc"] = False
            tc.variables["BUILD_examples"] = False
            tc.variables["BUILD_shared"] = self.options.shared
            tc.variables["BUILD_tests"] = False
            tc.variables["BUILD_tools"] = False
            # Generate a relocatable shared lib on Macos
            tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0042"] = "NEW"
        else:
            # These options were renamed in 2.2.8 to be more consistent
            tc.variables["EXPAT_BUILD_DOCS"] = False
            tc.variables["EXPAT_BUILD_EXAMPLES"] = False
            tc.variables["EXPAT_SHARED_LIBS"] = self.options.shared
            tc.variables["EXPAT_BUILD_TESTS"] = False
            tc.variables["EXPAT_BUILD_TOOLS"] = False
            # EXPAT_CHAR_TYPE was added in 2.2.8
            tc.variables["EXPAT_CHAR_TYPE"] = self.options.char_type
            if is_msvc(self):
                tc.variables["EXPAT_MSVC_STATIC_CRT"] = is_msvc_static_runtime(self)
        if Version(self.version) >= "2.2.10":
            tc.variables["EXPAT_BUILD_PKGCONFIG"] = False
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.set_property("cmake_find_mode", "both")
        self.cpp_info.set_property("cmake_module_file_name", "EXPAT")
        self.cpp_info.set_property("cmake_module_target_name", "EXPAT::EXPAT")
        self.cpp_info.set_property("cmake_file_name", "expat")
        self.cpp_info.set_property("cmake_target_name", "expat::expat")
        self.cpp_info.set_property("pkg_config_name", "expat")

        self.cpp_info.names["cmake_find_package"] = "EXPAT"
        self.cpp_info.names["cmake_find_package_multi"] = "expat"

        self.cpp_info.libs = collect_libs(self)
        if not self.options.shared:
            self.cpp_info.defines = ["XML_STATIC"]
        if self.options.get_safe("char_type") in ("wchar_t", "ushort"):
            self.cpp_info.defines.append("XML_UNICODE")
        elif self.options.get_safe("char_type") == "wchar_t":
            self.cpp_info.defines.append("XML_UNICODE_WCHAR_T")
