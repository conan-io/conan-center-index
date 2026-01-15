from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain,CMakeDeps, cmake_layout
from conan.tools.files import copy, get, replace_in_file
from conan.tools.build import check_min_cppstd
from conan.errors import ConanInvalidConfiguration
from conan.tools.scm import Version
import os

required_conan_version = ">=2.1"

class ClickHouseCppConan(ConanFile):
    name = "clickhouse-cpp"
    description = "ClickHouse C++ API"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/ClickHouse/clickhouse-cpp"
    topics = ("database", "db", "clickhouse")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_openssl": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_openssl": False,
    }
    implements = ["auto_shared_fpic"]

    @property
    def _requires_compiler_rt(self):
        return self.settings.compiler == "clang" and \
            ((self.settings.compiler.libcxx in ["libstdc++", "libstdc++11"] and not self.options.shared) or \
             self.settings.compiler.libcxx == "libc++")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("lz4/1.9.4")
        self.requires("abseil/[>=20230125.3 <=20250127.0]", transitive_headers=True)
        self.requires("cityhash/1.0.1")
        if self.options.with_openssl:
            self.requires("openssl/[>=1.1 <4]")

    def validate(self):
        check_min_cppstd(self, 17)
        abseil_cppstd = self.dependencies.host['abseil'].info.settings.compiler.cppstd
        if abseil_cppstd != self.settings.compiler.cppstd:
            raise ConanInvalidConfiguration(f"abseil must be built with the same compiler.cppstd setting")
        if self.settings.os == "Windows" and self.options.shared:
            raise ConanInvalidConfiguration(f"{self.ref} does not support shared library on Windows.")
            # look at https://github.com/ClickHouse/clickhouse-cpp/pull/226

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        # Let's avoid upstream setting the CMAKE_CXX_STANDARD 17
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"), "USE_CXX17", "# USE_CXX17")

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["BUILD_SHARED_LIBS"] = self.options.shared
        tc.cache_variables["WITH_OPENSSL"] = self.options.with_openssl
        tc.cache_variables["WITH_SYSTEM_ABSEIL"] = True
        tc.cache_variables["WITH_SYSTEM_LZ4"] = True
        tc.cache_variables["WITH_SYSTEM_CITYHASH"] = True
        tc.cache_variables["DEBUG_DEPENDENCIES"] = False
        if Version(self.version) <= "2.5.1":
            tc.cache_variables["CMAKE_POLICY_VERSION_MINIMUM"] = "3.5" # CMake 4 support
        tc.generate()

        cd = CMakeDeps(self)
        cd.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs.append("clickhouse-cpp-lib")
        self.cpp_info.set_property("cmake_target_name", "clickhouse-cpp-lib::clickhouse-cpp-lib")

        if self._requires_compiler_rt:
            ldflags = ["--rtlib=compiler-rt"]
            self.cpp_info.exelinkflags = ldflags
            self.cpp_info.sharedlinkflags = ldflags
            self.cpp_info.system_libs.append("gcc_s")

        if self.settings.os == 'Windows':
            self.cpp_info.system_libs = ['ws2_32', 'wsock32']
