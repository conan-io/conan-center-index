from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rmdir
import os

required_conan_version = ">=2.1"


class RedisPlusPlusConan(ConanFile):
    name = "redis-plus-plus"
    description = "Redis client written in C++"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/sewenew/redis-plus-plus"
    topics = ("database", "redis", "client", "tls")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_tls": [True, False],
        "build_async": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_tls": False,
        "build_async": False,
    }

    implements = ["auto_shared_fpic"]

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("hiredis/1.2.0", transitive_headers=True, transitive_libs=True)
        if self.options.build_async:
            self.requires("libuv/[>=1 <2]")

    def validate(self):
        check_min_cppstd(self, 11)

        if self.info.options.with_tls and not self.dependencies["hiredis"].options.with_ssl:
            raise ConanInvalidConfiguration(f"{self.name}/*:with_tls=True requires hiredis/*:with_ssl=True")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        apply_conandata_patches(self)

    def generate(self):
        tc = CMakeToolchain(self)
        cppstd = str(self.settings.compiler.cppstd).replace("gnu", "")
        tc.cache_variables["REDIS_PLUS_PLUS_CXX_STANDARD"] = cppstd
        tc.variables["REDIS_PLUS_PLUS_USE_TLS"] = self.options.with_tls
        if self.options.build_async:
            tc.cache_variables["REDIS_PLUS_PLUS_BUILD_ASYNC"] = "libuv"
        tc.variables["REDIS_PLUS_PLUS_BUILD_TEST"] = False
        tc.variables["REDIS_PLUS_PLUS_BUILD_STATIC"] = not self.options.shared
        tc.variables["REDIS_PLUS_PLUS_BUILD_SHARED"] = self.options.shared
        tc.variables["REDIS_PLUS_PLUS_BUILD_STATIC_WITH_PIC"] = self.options.shared
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "redis++")
        target_suffix = "" if self.options.shared else "_static"
        self.cpp_info.set_property("cmake_target_name", f"redis++::redis++{target_suffix}")
        self.cpp_info.set_property("pkg_config_name", "redis++")
        # TODO: back to global scope in conan v2
        lib_suffix = "_static" if self.settings.os == "Windows" and not self.options.shared else ""
        self.cpp_info.components["redis++lib"].libs = [f"redis++{lib_suffix}"]
        self.cpp_info.components["redis++lib"].requires = ["hiredis::hiredis"]
        if self.options.with_tls:
            self.cpp_info.components["redis++lib"].requires.append("hiredis::hiredis_ssl")
        if self.options.build_async:
            self.cpp_info.components["redis++lib"].requires.append("libuv::libuv")
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["redis++lib"].system_libs.append("pthread")
            self.cpp_info.components["redis++lib"].system_libs.append("m")

        self.cpp_info.components["redis++lib"].set_property("cmake_target_name", f"redis++::redis++{target_suffix}")
        self.cpp_info.components["redis++lib"].set_property("pkg_config_name", "redis++")
