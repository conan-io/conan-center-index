from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, replace_in_file, rmdir
from conan.tools.scm import Version
import os

required_conan_version = ">=1.53.0"


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

    @property
    def _min_cppstd(self):
        return "11" if Version(self.version) < "1.3.0" else "17"

    @property
    def _compilers_minimum_version(self):
        if Version(self.version) < "1.3.0":
            return {}
        return {
            "Visual Studio": "16",
            "msvc": "192",
            "gcc": "8",
            "clang": "7",
            "apple-clang": "12",
        }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if Version(self.version) < "1.3.0":
            del self.options.build_async

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("hiredis/1.1.0", transitive_headers=True)
        if self.options.get_safe("build_async"):
            self.requires("libuv/1.45.0")

    def validate(self):
        if self.info.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)

        minimum_version = self._compilers_minimum_version.get(str(self.info.settings.compiler), False)
        if minimum_version and Version(self.info.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support.",
            )

        if self.info.options.with_tls and not self.dependencies["hiredis"].options.with_ssl:
            raise ConanInvalidConfiguration(f"{self.name}:with_tls=True requires hiredis:with_ssl=True")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        if self.settings.compiler.get_safe("cppstd"):
            cppstd = str(self.settings.compiler.cppstd)
            if cppstd.startswith("gnu"):
                cppstd = cppstd[3:]
            tc.cache_variables["REDIS_PLUS_PLUS_CXX_STANDARD"] = cppstd
        tc.variables["REDIS_PLUS_PLUS_USE_TLS"] = self.options.with_tls
        if self.options.get_safe("build_async"):
            tc.cache_variables["REDIS_PLUS_PLUS_BUILD_ASYNC"] = "libuv"
        tc.variables["REDIS_PLUS_PLUS_BUILD_TEST"] = False
        tc.variables["REDIS_PLUS_PLUS_BUILD_STATIC"] = not self.options.shared
        tc.variables["REDIS_PLUS_PLUS_BUILD_SHARED"] = self.options.shared
        if Version(self.version) >= "1.2.3":
            tc.variables["REDIS_PLUS_PLUS_BUILD_STATIC_WITH_PIC"] = self.options.shared
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)
        if Version(self.version) < "1.2.3":
            replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"),
                                  "set_target_properties(${STATIC_LIB} PROPERTIES POSITION_INDEPENDENT_CODE ON)",
                                  "")

    def build(self):
        self._patch_sources()
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
        if self.options.get_safe("build_async"):
            self.cpp_info.components["redis++lib"].requires.append("libuv::libuv")
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["redis++lib"].system_libs.append("pthread")
            self.cpp_info.components["redis++lib"].system_libs.append("m")

        # TODO: to remove in conan v2
        self.cpp_info.names["cmake_find_package"] = "redis++"
        self.cpp_info.names["cmake_find_package_multi"] = "redis++"
        self.cpp_info.components["redis++lib"].names["cmake_find_package"] = f"redis++{target_suffix}"
        self.cpp_info.components["redis++lib"].names["cmake_find_package_multi"] = f"redis++{target_suffix}"
        self.cpp_info.components["redis++lib"].set_property("cmake_target_name", f"redis++::redis++{target_suffix}")
        self.cpp_info.components["redis++lib"].set_property("pkg_config_name", "redis++")
