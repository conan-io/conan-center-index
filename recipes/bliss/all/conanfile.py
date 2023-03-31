from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get
from conan.tools.microsoft import check_min_vs, is_msvc
import os

required_conan_version = ">=1.55.0"


class BlissConan(ConanFile):
    name = "bliss"
    description = "bliss is an open source tool for computing automorphism groups and canonical forms of graphs."
    topics = ("automorphism", "group", "graph")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://users.aalto.fi/~tjunttil/bliss"
    license = "GPL-3-or-later", "LGPL-3-or-later"
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_exact_int": [False, "gmp", "mpir"],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_exact_int": False,
    }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if self.options.with_exact_int == "gmp":
            # gmp is fully transitive through bignum.hh public header of bliss
            self.requires("gmp/6.2.1", transitive_headers=True, transitive_libs=True)
        elif self.options.with_exact_int == "mpir":
            self.requires("mpir/3.0.0", transitive_headers=True, transitive_libs=True)

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, 11)
        check_min_vs(self, "191")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["USE_GMP"] = self.options.with_exact_int != False
        tc.generate()
        if bool(self.options.with_exact_int):
            deps = CMakeDeps(self)
            deps.set_property(self.options.with_exact_int, "cmake_file_name", "gmp")
            deps.set_property(self.options.with_exact_int, "cmake_target_name", "gmp::gmp")
            deps.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "COPYING.LESSER", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["bliss" if self.options.shared else "bliss_static"]
        self.cpp_info.includedirs.append(os.path.join("include", "bliss"))
        if bool(self.options.with_exact_int):
            self.cpp_info.defines = ["BLISS_USE_GMP"]
        if is_msvc(self):
            self.cpp_info.cxxflags.append("/permissive-")
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")

        # TODO: to remove in conan v2
        self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))
