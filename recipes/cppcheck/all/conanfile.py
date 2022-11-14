from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, get, replace_in_file, rmdir
import os

required_conan_version = ">=1.33.0"


class CppcheckConan(ConanFile):
    name = "cppcheck"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/danmar/cppcheck"
    topics = ("Cpp Check", "static analyzer")
    description = "Cppcheck is an analysis tool for C/C++ code."
    license = "GPL-3.0-or-later"
    settings = "os", "arch", "compiler", "build_type"
    options = {"with_z3": [True, False], "have_rules": [True, False]}
    default_options = {"with_z3": True, "have_rules": True}
    exports_sources = ["CMakeLists.txt", "patches/**"]

    def layout(self):
        cmake_layout(self)

    def requirements(self):
        if self.options.with_z3:
            self.requires("z3/4.8.8")
        if self.options.have_rules:
            self.requires("pcre/8.45")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["USE_Z3"] = self.options.with_z3
        tc.variables["HAVE_RULES"] = self.options.have_rules
        tc.variables["USE_MATCHCOMPILER"] = "Auto"
        tc.variables["ENABLE_OSS_FUZZ"] = False
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        apply_conandata_patches(self)
        replace_in_file(self, os.path.join(self.source_folder, "cli", "CMakeLists.txt"),
                              "RUNTIME DESTINATION ${CMAKE_INSTALL_FULL_BINDIR}",
                              "DESTINATION ${CMAKE_INSTALL_FULL_BINDIR}")
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "COPYING", dst="licenses", src=self.source_folder)
        copy(self, "*", dst=os.path.join("bin", "cfg"), src=os.path.join(self.source_folder, "cfg"))
        copy(self, "cppcheck-htmlreport", dst=os.path.join("bin"), src=os.path.join(self.source_folder, "htmlreport"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.includedirs = []
        self.cpp_info.libdirs = []

        bin_folder = os.path.join(self.package_folder, "bin")
        self.output.info("Append %s to environment variable PATH" % bin_folder)
        self.buildenv_info.prepend_path("PATH", self.package_folder)
        self.buildenv_info.define_path("CPPCHECK_HTMLREPORT", os.path.join(bin_folder, "cppcheck-htmlreport"))
