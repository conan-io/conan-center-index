from conan import ConanFile
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get, copy, rmdir, rm, rename
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.apple import fix_apple_shared_install_name
import os

required_conan_version = ">=1.53.0"


class YAJLConan(ConanFile):
    name = "yajl"
    description = "A fast streaming JSON parsing library in C"
    license = "ISC"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/lloyd/yajl"
    topics = ("json", "encoding", "decoding", "manipulation")
    package_type = "library"
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
        get(self, **self.conan_data["sources"][self.version], destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="COPYING", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()

        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        rm(self, "*.la", os.path.join(self.package_folder, "lib"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "lib"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "bin"))

        # We need to move the dll from lib to bin in order for it to be found later
        if self.settings.os == "Windows":
            rename(self, os.path.join(self.package_folder, "lib", "yajl.dll"), os.path.join(self.package_folder, "bin", "yajl.dll"))
        fix_apple_shared_install_name(self)

    def package_info(self):
        self.cpp_info.libs = ["yajl"]

        self.cpp_info.set_property("cmake_file_name", "yajl")
        self.cpp_info.set_property("cmake_target_name", "yajl::yajl")
        self.cpp_info.set_property("pkg_config_name", "yajl")

        if self.options.shared:
            self.cpp_info.libs = ["yajl"]
        else:
            self.cpp_info.libs = ["yajl_s"]

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "YAJL"
        self.cpp_info.filenames["cmake_find_package_multi"] = "yajl"
        self.cpp_info.names["cmake_find_package"] = "YAJL"
        self.cpp_info.names["cmake_find_package_multi"] = "yajl"
