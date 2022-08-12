from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, collect_libs, copy, get, rmdir
from conan.tools.microsoft import is_msvc, msvc_runtime_flag
import os

required_conan_version = ">=1.50.0"


class UriparserConan(ConanFile):
    name = "uriparser"
    description = "Strictly RFC 3986 compliant URI parsing and handling library written in C89"
    topics = ("uriparser", "URI", "parser")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://uriparser.github.io/"

    license = "BSD-3-Clause"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_char": [True, False],
        "with_wchar": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_char": True,
        "with_wchar": True,
    }

    def export_sources(self):
        for p in self.conan_data.get("patches", {}).get(self.version, []):
            copy(self, p["patch_file"], self.recipe_folder, self.export_sources_folder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        try:
           del self.settings.compiler.libcxx
        except Exception:
           pass
        try:
           del self.settings.compiler.cppstd
        except Exception:
           pass

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["URIPARSER_BUILD_DOCS"] = False
        tc.variables["URIPARSER_BUILD_TESTS"] = False
        tc.variables["URIPARSER_BUILD_TOOLS"] = False
        tc.variables["URIPARSER_BUILD_CHAR"] = self.options.with_char
        tc.variables["URIPARSER_BUILD_WCHAR"] = self.options.with_wchar
        if is_msvc(self):
            tc.variables["URIPARSER_MSVC_RUNTIME"] = f"/{msvc_runtime_flag(self)}"
        # Honor BUILD_SHARED_LIBS (see https://github.com/conan-io/conan/issues/11840)
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0077"] = "NEW"
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

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "liburiparser")
        self.cpp_info.libs = collect_libs(self)
        if not self.options.shared:
            self.cpp_info.defines.append("URI_STATIC_BUILD")
        if not self.options.with_char:
            self.cpp_info.defines.append("URI_NO_ANSI")
        if not self.options.with_wchar:
            self.cpp_info.defines.append("URI_NO_UNICODE")

        # TODO: to remove in conan v2 once pkg_config generator removed
        self.cpp_info.names["pkg_config"] = "liburiparser"
