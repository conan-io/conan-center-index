from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get
import os

required_conan_version = ">=2.1"


class CppcheckConan(ConanFile):
    name = "cppcheck"
    description = "Cppcheck is an analysis tool for C/C++ code."
    license = "GPL-3.0-or-later"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/danmar/cppcheck"
    topics = ("code quality", "static analyzer", "linter")
    package_type = "application"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "have_rules": [True, False],
    }
    default_options = {
        "have_rules": True,
    }

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if self.options.have_rules:
            self.requires("pcre/8.45")
    
    def build_requirements(self):
        self.tool_requires("cmake/[>=3.22]")

    def package_id(self):
        del self.info.settings.compiler
        del self.info.settings.build_type

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        apply_conandata_patches(self)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["HAVE_RULES"] = self.options.have_rules
        tc.variables["USE_MATCHCOMPILER"] = "Auto"
        tc.variables["ENABLE_OSS_FUZZ"] = False
        tc.variables["DISABLE_DMAKE"] = True
        tc.variables["FILESDIR"] = "bin"
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "COPYING", dst=os.path.join(self.package_folder, "licenses"), src=os.path.join(self.source_folder))
        copy(self, "cppcheck-htmlreport", dst=os.path.join(self.package_folder, "bin"), src=os.path.join(self.source_folder, "htmlreport"))
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.includedirs = []
        self.cpp_info.libdirs = []

        bin_folder = os.path.join(self.package_folder, "bin")
        cppcheck_htmlreport = os.path.join(bin_folder, "cppcheck-htmlreport")
        self.runenv_info.define_path("CPPCHECK_HTMLREPORT", cppcheck_htmlreport)
