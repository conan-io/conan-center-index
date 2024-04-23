from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, replace_in_file
from conan.tools.scm import Version
import os

required_conan_version = ">=1.52.0"


class CppcheckConan(ConanFile):
    name = "cppcheck"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/danmar/cppcheck"
    topics = ("code quality", "static analyzer", "linter")
    description = "Cppcheck is an analysis tool for C/C++ code."
    license = "GPL-3.0-or-later"
    package_type = "application"
    settings = "os", "arch", "compiler", "build_type"
    options = {"have_rules": [True, False]}
    default_options = {"have_rules": True}

    def layout(self):
        cmake_layout(self, src_folder="src")

    @property
    def _min_cppstd(self):
        return 11

    def validate(self):
        if self.settings.get_safe("compiler.cppstd"):
            check_min_cppstd(self, self._min_cppstd)

    def export_sources(self):
        export_conandata_patches(self)

    def requirements(self):
        if self.options.get_safe("have_rules"):
            self.requires("pcre/8.45")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["HAVE_RULES"] = self.options.get_safe("have_rules", False)
        tc.variables["USE_MATCHCOMPILER"] = "Auto"
        tc.variables["ENABLE_OSS_FUZZ"] = False
        if Version(self.version) >= "2.11.0":
            tc.variables["DISABLE_DMAKE"] = True
        tc.variables["FILESDIR"] = "bin"
        # TODO: Remove when Conan 1 support is dropped
        if not self.settings.get_safe("compiler.cppstd"):
            tc.variables["CMAKE_CXX_STANDARD"] = self._min_cppstd
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)
        if Version(self.version) >= "2.14":
            replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"), "use_cxx11()", "")

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "COPYING", dst=os.path.join(self.package_folder, "licenses"), src=os.path.join(self.source_folder))
        copy(self, "cppcheck-htmlreport", dst=os.path.join(self.package_folder, "bin"), src=os.path.join(self.source_folder, "htmlreport"))
        cmake = CMake(self)
        cmake.install()

    def package_id(self):
        del self.info.settings.compiler
        del self.info.settings.build_type

    def package_info(self):
        self.cpp_info.includedirs = []
        self.cpp_info.libdirs = []

        bin_folder = os.path.join(self.package_folder, "bin")
        self.env_info.PATH.append(bin_folder)

        cppcheck_htmlreport = os.path.join(bin_folder, "cppcheck-htmlreport")
        self.env_info.CPPCHECK_HTMLREPORT = cppcheck_htmlreport
        self.runenv_info.define_path("CPPCHECK_HTMLREPORT", cppcheck_htmlreport)
