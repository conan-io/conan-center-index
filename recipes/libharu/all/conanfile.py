from conan import ConanFile
from conan.tools.microsoft import is_msvc
from conan.tools.files import get, copy, rm, rmdir, load, save
from conan.tools.scm import Version
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
import os
import re


required_conan_version = ">=1.53.0"



class LibharuConan(ConanFile):
    name = "libharu"
    description = "Haru is a free, cross platform, open-sourced software library for generating PDF."
    topics = "pdf", "generate", "generator"
    license = "Zlib"
    homepage = "http://libharu.org/"
    url = "https://github.com/conan-io/conan-center-index"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def layout(self):
        # src_folder must use the same source folder name the project
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("zlib/[>=1.2.11 <2]")
        self.requires("libpng/[>=1.6 <2]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["LIBHPDF_SHARED"] = self.options.shared
        tc.variables["LIBHPDF_STATIC"] = not self.options.shared
        # Honor BUILD_SHARED_LIBS from conan_toolchain (see https://github.com/conan-io/conan/issues/11840)
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0077"] = "NEW"
        tc.generate()
        tc = CMakeDeps(self)
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def _v230_extract_license(self):
        readme = load(save, os.path.join(self.source_folder, "README"))
        match = next(re.finditer("\n[^\n]*license[^\n]*\n", readme, flags=re.I | re.A))
        return readme[match.span()[1]:].strip("*").strip()

    def package(self):
        cmake = CMake(self)
        cmake.install()

        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        libprefix = ""
        libsuffix = ""
        self.cpp_info.libs = [f"{libprefix}hpdf{libsuffix}"]
        if self.settings.os == "Windows" and self.options.shared:
            self.cpp_info.defines = ["HPDF_DLL"]
        if self.settings.os in ["Linux", "FreeBSD"] and not self.options.shared:
            self.cpp_info.system_libs = ["m"]
