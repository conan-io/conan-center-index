from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get, rmdir
from conan.tools.cmake import cmake_layout, CMakeToolchain, CMake, CMakeDeps
import os


class MexceConan(ConanFile):
    name = "mexce"
    license = "BSD-2-Clause"
    homepage = "https://github.com/imakris/mexce"
    url = "https://github.com/conan-io/conan-center-index"
    description = "Single-header, dependency-free JIT compiler for scalar mathematical expressions."
    topics = ("jit", "math", "expression-parser", "header-only")
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    options = {"with_protected": [True, False]}
    default_options = {"with_protected": False}

    def requirements(self):
        if self.options.with_protected:
            self.requires("libsodium/[~1.0.22]")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def validate(self):
        check_min_cppstd(self, 11)
        supported_archs = ["x86_64", "armv8"] if self.settings.os == "Macos" else ["x86", "x86_64"]
        if str(self.settings.arch) not in supported_archs:
            raise ConanInvalidConfiguration("Not supported architecture. See https://github.com/imakris/mexce#requirements")
        if self.options.with_protected and self.settings.arch == "x86":
            raise ConanInvalidConfiguration("with_protected requires x86_64 or armv8. See https://github.com/imakris/mexce/blob/master/docs/protected_expressions.md")

    def package_id(self):
        self.info.settings.clear()

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["MEXCE_ENABLE_PROTECTED_EXPRESSIONS"] = self.options.with_protected
        tc.cache_variables["BUILD_TESTING"] = False
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        copy(self, "LICENSE*", self.source_folder,
             os.path.join(self.package_folder, "licenses"))
        if self.options.with_protected:
            copy(self, "THIRD_PARTY_NOTICES.md", self.source_folder,
                 os.path.join(self.package_folder, "licenses"))

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "none")
        self.cpp_info.set_property("cmake_target_name", "none")
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.components["mexce"].bindirs = []
        self.cpp_info.components["mexce"].libdirs = []
        self.cpp_info.components["mexce"].set_property("cmake_target_name", "mexce::mexce")
        self.cpp_info.components["mexce"].set_property("pkg_config_name", "mexce")
        if self.options.with_protected:
            self.cpp_info.components["protected"].bindirs = []
            self.cpp_info.components["protected"].libdirs = []
            self.cpp_info.components["protected"].set_property("cmake_target_name", "mexce::protected")
            self.cpp_info.components["protected"].set_property("pkg_config_name", "mexce-protected")
            self.cpp_info.components["protected"].requires = ["mexce", "libsodium::libsodium"]
