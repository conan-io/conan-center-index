from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import collect_libs, copy, get, rmdir
import os


required_conan_version = ">=2.1"


class ZlinkConan(ConanFile):
    name = "zlink"
    description = "High-performance asynchronous messaging library"
    license = "MPL-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/zlink-systems/zlink"
    topics = ("messaging", "networking", "ipc", "asynchronous")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_tls": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_tls": True,
    }
    implements = ["auto_shared_fpic"]

    def layout(self):
        cmake_layout(self)

    def requirements(self):
        if self.options.with_tls:
            self.requires("openssl/[>=3.0 <4]")

    def validate(self):
        check_min_cppstd(self, 17)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=False)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["BUILD_SHARED"] = bool(self.options.shared)
        tc.cache_variables["BUILD_STATIC"] = not bool(self.options.shared)
        # Upstream enables LTO/IPO by default; a static library built with
        # -flto forces the consumer's toolchain to load the LTO plugin at link
        # time, so leave IPO to the consumer.
        tc.cache_variables["ENABLE_LTO"] = False
        tc.cache_variables["BUILD_TESTS"] = False
        tc.cache_variables["BUILD_BENCHMARKS"] = False
        tc.cache_variables["WITH_DOC"] = False
        tc.cache_variables["ENABLE_CPACK"] = False
        tc.cache_variables["WITH_TLS"] = bool(self.options.with_tls)
        tc.cache_variables["WITH_LIBBSD"] = False
        tc.cache_variables["ZLINK_CXX_STANDARD"] = "17"
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure(build_script_folder=os.path.join(self.source_folder, "core"))
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        cmake_target = "libzlink" if self.options.shared else "libzlink-static"
        self.cpp_info.set_property("cmake_file_name", "zlink")
        self.cpp_info.set_property("cmake_target_name", cmake_target)
        self.cpp_info.set_property("pkg_config_name", "libzlink")
        self.cpp_info.libs = collect_libs(self)
        if not self.options.shared:
            self.cpp_info.defines.append("ZLINK_STATIC")
        if self.options.with_tls:
            self.cpp_info.requires.append("openssl::openssl")
        if self.settings.os == "Windows":
            self.cpp_info.system_libs.extend(["ws2_32", "rpcrt4", "iphlpapi"])
            if self.options.with_tls:
                self.cpp_info.system_libs.append("crypt32")
        elif self.settings.os in ("Linux", "FreeBSD"):
            self.cpp_info.system_libs.extend(["m", "pthread", "rt"])
