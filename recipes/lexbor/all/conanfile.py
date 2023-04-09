from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.microsoft import check_min_vs, is_msvc_static_runtime, is_msvc
from conan.tools.files import get, copy, rm
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
import os

required_conan_version = ">=1.53.0"

class LexborConan(ConanFile):
    name = "lexbor"
    description = "Lexbor is development of an open source HTML Renderer library"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/lexbor/lexbor/"
    topics = ("html5", "css", "parser", "renderer")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "build_separately": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "build_separately": False,
    }

    @property
    def _is_mingw(self):
        return self.settings.os == "Windows" and self.settings.compiler == "gcc"

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

    def validate(self):
        # static build on Windows will be support by future release. (https://github.com/lexbor/lexbor/issues/69)
        if str(self.version) == "2.1.0" and self.options.shared == False and (is_msvc(self) or self._is_mingw):
            raise ConanInvalidConfiguration(f"{self.ref} doesn't support static build on Windows(please use 2.2.0).")

        if self.options.build_separately:
            raise ConanInvalidConfiguration(f"{self.ref} doesn't support build_separately option(yet).")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["LEXBOR_BUILD_SHARED"] = self.options.shared
        tc.cache_variables["LEXBOR_BUILD_STATIC"] = not self.options.shared
        tc.variables["LEXBOR_TESTS_CPP"] = False
        tc.variables["LEXBOR_BUILD_SEPARATELY"] = self.options.build_separately
        tc.variables["LEXBOR_INSTALL_HEADERS"] = True
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        target = "lexbor" if self.options.shared else "lexbor_static"
        self.cpp_info.set_property("cmake_file_name", "lexbor")
        self.cpp_info.set_property("cmake_target_name", f"lexbor::{target}")
        self.cpp_info.names["cmake_find_package"] = "lexbor"
        self.cpp_info.names["cmake_find_package_multi"] = "lexbor"

        self.cpp_info.components["_lexbor"].set_property("cmake_target_name", f"lexbor::{target}")
        self.cpp_info.components["_lexbor"].names["cmake_find_package"] = target
        self.cpp_info.components["_lexbor"].names["cmake_find_package_multi"] = target

        self.cpp_info.components["_lexbor"].libs = [target]
        self.cpp_info.components["_lexbor"].defines = ["LEXBOR_BUILD_SHARED" if self.options.shared else "LEXBOR_BUILD_STATIC"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["_lexbor"].system_libs.append("m")

