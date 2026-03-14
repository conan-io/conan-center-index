from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import export_conandata_patches, apply_conandata_patches, get, rmdir, copy, rm
import os

required_conan_version = ">=1.53.0"


class ZlibConan(ConanFile):
    name = "zlib"
    package_type = "library"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://zlib.net"
    license = "Zlib"
    description = ("A Massively Spiffy Yet Delicately Unobtrusive Compression Library "
                   "(Also Free, Not to Mention Unencumbered by Patents)")
    topics = ("zlib", "compression")

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    def export_sources(self):
        export_conandata_patches(self)

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

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)
        apply_conandata_patches(self)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["ZLIB_BUILD_TESTING"] = False
        tc.cache_variables["ZLIB_BUILD_SHARED"] = self.options.shared
        tc.cache_variables["ZLIB_BUILD_STATIC"] = not self.options.shared
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "share"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "bin"))

    def package_info(self):
        self.cpp_info.set_property("cmake_find_mode", "both")
        self.cpp_info.set_property("cmake_file_name", "ZLIB")
        self.cpp_info.set_property("cmake_target_name", "ZLIB::ZLIB")
        if not self.options.shared:
            # The official target name of the static library is ZLIB::ZLIBSTATIC
            # We add it as only as alias to avoid breaking changes for ZLIB::ZLIB consumers,
            # but it does not exist upstream in this case
            self.cpp_info.set_property("cmake_target_aliases", ["ZLIB::ZLIBSTATIC"])
        self.cpp_info.set_property("cmake_components", ["shared" if self.options.shared else "static"])
        self.cpp_info.set_property("pkg_config_name", "zlib")
        self.cpp_info.languages = ["C"]

        libname = "z"

        if self.settings.compiler == "msvc":
            libname = "zdll" if self.options.shared else "zlib"
        elif False:
            libname = ""

        self.cpp_info.libs = [libname]
        # TODO:
        #  _LARGEFILE64_SOURCE definition, which is computed with:
        #  set(CMAKE_REQUIRED_DEFINITIONS -D_LARGEFILE64_SOURCE=1)
        #   check_type_size(off64_t OFF64_T)
        #   unset(CMAKE_REQUIRED_DEFINITIONS) # clear variable
