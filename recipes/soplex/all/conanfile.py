from conan import ConanFile
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import get, rm, rmdir, apply_conandata_patches, export_conandata_patches, copy
import os

required_conan_version = ">=2.4"


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
        # transitive libs as anything using soplex requires gzread, gzwrite, gzclose, gzopen
        self.requires("zlib/[>=1.2.11 <2]", transitive_headers=True, transitive_libs=True)
        if self.options.with_gmp:
            # transitive libs as anything using soplex requires __gmpz_init_set_si
            # see https://github.com/conan-io/conan-center-index/pull/16017#issuecomment-1495688452
            self.requires("gmp/6.3.0", transitive_headers=True, transitive_libs=True)
        if self.options.with_boost:
            self.requires("boost/1.84.0", transitive_headers=True)  # also update Boost_VERSION_MACRO below!
        self.requires("fmt/[>=11 <13]", transitive_headers=True)
        self.requires("zstr/[>1 <2]", transitive_headers=True)

    def validate(self):
        check_min_cppstd(self, 14)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        # Vendorized fmt and zstr
        rmdir(self, os.path.join(self.source_folder, "src", "soplex", "external"))
        apply_conandata_patches(self)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["MPFR"] = False
        tc.cache_variables["GMP"] = self.options.with_gmp
        tc.cache_variables["BOOST"] = self.options.with_boost
        tc.cache_variables["Boost_VERSION_MACRO"] = "108400"
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0077"] = "NEW"
        tc.generate()
        deps = CMakeDeps(self)
        if self.options.with_gmp:
            deps.set_property("gmp", "cmake_file_name", "GMP")
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        if self.options.shared:
            rm(self, "*.lib", os.path.join(self.package_folder, "lib"), excludes=["libsoplexshared*"])
            rm(self, "*.a", os.path.join(self.package_folder, "lib"))
        else:
            rm(self, "*.so*", os.path.join(self.package_folder, "lib"))
            rm(self, "*.dylib*", os.path.join(self.package_folder, "lib"))
            rm(self, "*.dll*", os.path.join(self.package_folder, "bin"))
            excludes = ["libsoplex-pic.*"] if self.options.get_safe("fPIC") else ["libsoplex.*"]
            rm(self, "*.lib", os.path.join(self.package_folder, "lib"), excludes=excludes)
            rm(self, "*.a", os.path.join(self.package_folder, "lib"), excludes=excludes)

        rm(self, "soplex.exe" if self.settings.os == "Windows" else "soplex",
           os.path.join(self.package_folder, "bin"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        fix_apple_shared_install_name(self)

    def package_info(self):
        if self.options.shared:
            libname = "soplexshared"
        elif self.options.get_safe("fPIC"):
            libname = "soplex-pic"
        else:
            libname = "soplex"

        self.cpp_info.libs = [libname]
        # https://github.com/conan-io/conan-center-index/pull/16017#discussion_r1156484737
        self.cpp_info.set_property("cmake_target_name", "soplex")
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")
