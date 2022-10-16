from conan import ConanFile
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rmdir
import os

required_conan_version = ">=1.52.0"


class HiredisConan(ConanFile):
    name = "hiredis"
    description = "Hiredis is a minimalistic C client library for the Redis database."
    license = "BSD-3-Clause"
    topics = ("hiredis", "redis", "client", "database")
    homepage = "https://github.com/redis/hiredis"
    url = "https://github.com/conan-io/conan-center-index"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_ssl": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_ssl": False,
    }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            try:
                del self.options.fPIC
            except Exception:
                pass
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

    def requirements(self):
        if self.options.with_ssl:
            self.requires("openssl/1.1.1q")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["ENABLE_SSL"] = self.options.with_ssl
        tc.variables["DISABLE_TESTS"] = True
        tc.variables["ENABLE_EXAMPLES"] = False
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "hiredis")

        # hiredis
        self.cpp_info.components["hiredislib"].set_property("cmake_target_name", "hiredis::hiredis")
        self.cpp_info.components["hiredislib"].set_property("pkg_config_name", "hiredis")
        self.cpp_info.components["hiredislib"].names["cmake_find_package"] = "hiredis"
        self.cpp_info.components["hiredislib"].names["cmake_find_package_multi"] = "hiredis"
        self.cpp_info.components["hiredislib"].libs = ["hiredis"]
        if self.settings.os == "Windows":
            self.cpp_info.components["hiredislib"].system_libs = ["ws2_32"]
        # hiredis_ssl
        if self.options.with_ssl:
            self.cpp_info.components["hiredis_ssl"].set_property("cmake_target_name", "hiredis::hiredis_ssl")
            self.cpp_info.components["hiredis_ssl"].set_property("pkg_config_name", "hiredis_ssl")
            self.cpp_info.components["hiredis_ssl"].names["cmake_find_package"] = "hiredis_ssl"
            self.cpp_info.components["hiredis_ssl"].names["cmake_find_package_multi"] = "hiredis_ssl"
            self.cpp_info.components["hiredis_ssl"].libs = ["hiredis_ssl"]
            self.cpp_info.components["hiredis_ssl"].requires = ["openssl::ssl"]
            if self.settings.os == "Windows":
                self.cpp_info.components["hiredis_ssl"].requires.append("hiredislib")

            # These cmake_target_name and pkg_config_name are unofficial. It avoids conflicts
            # in conan generators between global target/pkg-config and hiredislib component.
            # TODO: eventually remove the cmake_target_name trick if conan can implement smarter logic
            # in CMakeDeps when a downstream recipe requires another recipe globally
            # (link to all components directly instead of global target)
            self.cpp_info.set_property("cmake_target_name", "hiredis::hiredis_all_unofficial")
            self.cpp_info.set_property("pkg_config_name", "hiredis_all_unofficial")
