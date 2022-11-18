from conan import ConanFile
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get, copy, rmdir, replace_in_file
from conan.tools.build import check_min_cppstd
from conan.tools.scm import Version
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout

import os

required_conan_version = ">=1.53.0"

class CppcheckConan(ConanFile):
    name = "cppcheck"
    description = "Cppcheck is an analysis tool for C/C++ code."
    license = "GPL-3.0-or-later"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/danmar/cppcheck"
    topics = ("Cpp Check", "static analyzer")
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "with_z3": [True, False],
        "have_rules": [True, False],
        "with_threads": [True, False],
        "with_boost": [True, False],
    }
    default_options = {
        "with_z3": True,
        "have_rules": True,
        "with_threads": False,
        "with_boost": False,
    }

    @property
    def _min_cppstd(self):
        return 11

    def config_options(self):
        if Version(self.version) < "2.8":
            del self.options.with_threads
            del self.options.with_boost
        else:
            del self.options.with_z3

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if self.options.get_safe("with_z3"):
            self.requires("z3/4.10.2")
        if self.options.have_rules:
            self.requires("pcre/8.45")
        self.requires("tinyxml2/9.0.0")
        if self.options.get_safe("with_boost"):
            self.requires("boost/1.80.0")

    def validate(self):
        if self.info.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        if "with_z3" in self.options:
            tc.variables["USE_Z3"] = self.options.with_z3
        tc.variables["HAVE_RULES"] = self.options.have_rules
        # TODO: force disable until cpython requires latest zlib (which conflicts other dependencies)
        tc.variables["USE_MATCHCOMPILER"] = "Off"
        tc.variables["ENABLE_OSS_FUZZ"] = False
        tc.variables["USE_BUNDLED_TINYXML2"] = False
        if "with_threads" in self.options:
            tc.variables["USE_THREADS"] = self.options.with_threads
        if "with_boost" in self.options:
            tc.variables["USE_BOOST"] = self.options.with_boost
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)
        replace_in_file(self, os.path.join(self.source_folder, "cli", "CMakeLists.txt"),
                        "RUNTIME DESTINATION ${CMAKE_INSTALL_FULL_BINDIR}",
                        "DESTINATION ${CMAKE_INSTALL_FULL_BINDIR}")

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="COPYING", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)

        copy(self, "*", dst=os.path.join(self.package_folder, "bin", "cfg"), src=os.path.join(self.source_folder,"cfg"))
        copy(self, "cppcheck-htmlreport", dst=os.path.join(self.package_folder, "bin"), src=os.path.join(self.source_folder,"htmlreport"))

        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        bin_folder = os.path.join(self.package_folder, "bin")
        self.output.info(f"Append {bin_folder} to environment variable PATH")
        self.env_info.PATH.append(bin_folder)
        # This is required to run the python script on windows, as we cannot simply add it to the PATH
        self.env_info.CPPCHECK_HTMLREPORT = os.path.join(bin_folder, "cppcheck-htmlreport")
