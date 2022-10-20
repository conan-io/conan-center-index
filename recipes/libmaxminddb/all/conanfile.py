from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, get, rmdir
import os

required_conan_version = ">=1.50.0"


class LibmaxminddbConan(ConanFile):
    name = "libmaxminddb"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://maxmind.github.io/libmaxminddb/"
    description = "C library for the MaxMind DB file format"
    topics = ("maxmind", "geoip")

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
        tc.variables["BUILD_TESTING"] = False
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

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "maxminddb")
        self.cpp_info.set_property("cmake_target_name", "maxminddb::maxminddb")
        self.cpp_info.set_property("pkg_config_name", "libmaxminddb")
        self.cpp_info.libs = ["maxminddb"]
        if self.settings.os == "Windows":
            self.cpp_info.system_libs = ["ws2_32"]

        if self.settings.os != "Windows":
            bin_path = os.path.join(self.package_folder, "bin")
            self.output.info(f"Appending PATH environment variable: {bin_path}")
            self.env_info.PATH.append(bin_path)

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.names["cmake_find_package"] = "maxminddb"
        self.cpp_info.names["cmake_find_package_multi"] = "maxminddb"
