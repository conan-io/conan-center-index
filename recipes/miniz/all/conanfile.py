from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, get, rmdir
from conan.tools.scm import Version
import os

required_conan_version = ">=1.50.0"


class MinizConan(ConanFile):
    name = "miniz"
    description = "Lossless, high performance data compression library that " \
                  "implements the zlib (RFC 1950) and Deflate (RFC 1951) " \
                  "compressed data format specification standards"
    license = "MIT"
    topics = ("miniz", "compression", "lossless")
    homepage = "https://github.com/richgel999/miniz"
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

    def export_sources(self):
        for p in self.conan_data.get("patches", {}).get(self.version, []):
            copy(self, p["patch_file"], self.recipe_folder, self.export_sources_folder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        try:
            del self.settings.compiler.libcxx
        except Exception:
            pass
        try:
            del self.settings.compiler.cppstd
        except Exception:
            pass

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        if Version(self.version) >= "2.2.0":
            tc.variables["BUILD_EXAMPLES"] = False
            tc.variables["BUILD_FUZZERS"] = False
            tc.variables["AMALGAMATE_SOURCES"] = False
            tc.variables["BUILD_HEADER_ONLY"] = False
            tc.variables["INSTALL_PROJECT"] = True
        # Honor BUILD_SHARED_LIBS from conan_toolchain (see https://github.com/conan-io/conan/issues/11840)
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0077"] = "NEW"
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "miniz")
        self.cpp_info.set_property("cmake_target_name", "miniz::miniz")
        self.cpp_info.set_property("pkg_config_name", "miniz")
        self.cpp_info.libs = ["miniz"]
        self.cpp_info.includedirs.append(os.path.join("include", "miniz"))
