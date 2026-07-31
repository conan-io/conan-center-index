from conan import ConanFile
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import (collect_libs, copy, get, apply_conandata_patches,
                               export_conandata_patches, replace_in_file)
import os

required_conan_version = ">=2"


class SoPlexConan(ConanFile):
    name = "soplex"
    description = "SoPlex linear programming solver"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://soplex.zib.de"
    topics = ("simplex", "solver", "linear", "programming")
    settings = "os", "arch", "compiler", "build_type"
    package_type = "library"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_boost": [True, False],
        "with_gmp": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_boost": True,
        "with_gmp": True,
    }

    def _determine_lib_name(self):
        if self.options.shared:
            return "soplexshared"
        elif self.options.get_safe("fPIC"):
            return "soplex-pic"
        else:
            return "soplex"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        # transitive libs as anything using soplex requires gzread, gzwrite, gzclose, gzopen
        self.requires("zlib/[>=1.2.11 <2]", transitive_headers=True, transitive_libs=True)
        if self.options.with_gmp:
            # transitive libs as anything using soplex requires __gmpz_init_set_si
            # see https://github.com/conan-io/conan-center-index/pull/16017#issuecomment-1495688452
            self.requires("gmp/6.3.0", transitive_headers=True, transitive_libs=True)
        if self.options.with_boost:
            self.requires("boost/1.84.0", transitive_headers=True)  # also update Boost_VERSION_MACRO below!

    def export_sources(self):
        export_conandata_patches(self)

    def validate(self):
        check_min_cppstd(self, 14)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"), "set(CMAKE_CXX_STANDARD", "##")

    def generate(self):
        apply_conandata_patches(self)
        tc = CMakeToolchain(self)
        tc.variables["MPFR"] = False
        tc.variables["GMP"] = self.options.with_gmp
        tc.variables["BOOST"] = self.options.with_boost
        tc.variables["Boost_VERSION_MACRO"] = "108400"
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0077"] = "NEW"
        tc.generate()
        deps = CMakeDeps(self)
        if self.options.with_gmp:
            deps.set_property("gmp", "cmake_file_name", "GMP")
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build(target=f"lib{self._determine_lib_name()}")

    def package(self):
        src_folder = os.path.join(self.source_folder, "src")
        include_folder = os.path.join(self.package_folder, "include")
        build_lib_folder = os.path.join(self.build_folder, "lib")
        pkg_lib_folder = os.path.join(self.package_folder, "lib")
        copy(self, pattern="LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, pattern="soplex.h", src=src_folder, dst=include_folder)
        copy(self, pattern="soplex.hpp", src=src_folder, dst=include_folder)
        copy(self, pattern="soplex_interface.h", src=src_folder, dst=include_folder)
        copy(self, pattern="*.h", src=os.path.join(src_folder, "soplex"), dst=os.path.join(include_folder, "soplex"))
        copy(self, pattern="*.hpp", src=os.path.join(src_folder, "soplex"), dst=os.path.join(include_folder, "soplex"))
        copy(self, pattern="*.h", src=os.path.join(self.build_folder, "soplex"), dst=os.path.join(include_folder, "soplex"))
        copy(self, pattern="*.lib", src=build_lib_folder, dst=pkg_lib_folder, keep_path=False)
        if self.options.shared:
            copy(self, pattern="*.so*", src=build_lib_folder, dst=pkg_lib_folder, keep_path=False)
            copy(self, pattern="*.dylib*", src=build_lib_folder, dst=pkg_lib_folder, keep_path=False)
            copy(self, pattern="*.dll", src=os.path.join(self.build_folder, "bin"), dst=os.path.join(self.package_folder, "bin"), keep_path=False)
            copy(self, pattern="*.dll.a", src=build_lib_folder, dst=pkg_lib_folder, keep_path=False)
        else:
            copy(self, pattern="*.a", src=build_lib_folder, dst=pkg_lib_folder, keep_path=False)
        fix_apple_shared_install_name(self)

    def package_info(self):
        self.cpp_info.libs = collect_libs(self)
        # https://github.com/conan-io/conan-center-index/pull/16017#discussion_r1156484737
        self.cpp_info.set_property("cmake_target_name", "soplex")
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")
