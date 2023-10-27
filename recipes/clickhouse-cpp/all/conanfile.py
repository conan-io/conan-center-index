from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain,CMakeDeps, cmake_layout
from conan.tools.files import copy, get
from conan.tools.build import check_min_cppstd
from conan.errors import ConanInvalidConfiguration
from conan.tools.scm import Version
import os

required_conan_version = ">=1.53.0"

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

    @property
    def _min_cppstd(self):
        return "17"

    @property
    def _compilers_minimum_version(self):
        return {
            "Visual Studio": "15",
            "msvc": "191",
            "gcc": "7",
            "clang": "6",
        }

    @property
    def _requires_compiler_rt(self):
        return self.settings.compiler == "clang" and \
            ((self.settings.compiler.libcxx in ["libstdc++", "libstdc++11"] and not self.options.shared) or \
             self.settings.compiler.libcxx == "libc++")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("lz4/1.9.4")
        self.requires("abseil/20230125.3", transitive_headers=True)
        self.requires("cityhash/cci.20130801")
        if self.options.with_openssl:
            self.requires("openssl/[>=1.1 <4]")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support.")
        if self.settings.os == "Windows" and self.options.shared:
            raise ConanInvalidConfiguration(f"{self.ref} does not support shared library on Windows.")
            # look at https://github.com/ClickHouse/clickhouse-cpp/pull/226

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["BUILD_SHARED_LIBS"] = self.options.shared
        tc.cache_variables["WITH_OPENSSL"] = self.options.with_openssl
        tc.cache_variables["WITH_SYSTEM_ABSEIL"] = True
        tc.cache_variables["WITH_SYSTEM_LZ4"] = True
        tc.cache_variables["WITH_SYSTEM_CITYHASH"] = True
        # TODO: enable DEBUG_DEPENDENCIES on >= 2.5.0
        if Version(self.version) >= "2.5.0":
            tc.cache_variables["DEBUG_DEPENDENCIES"] = False
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

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "clickhouse-cpp"
        self.cpp_info.filenames["cmake_find_package_multi"] = "clickhouse-cpp"
        self.cpp_info.names["cmake_find_package"] = "clickhouse-cpp-lib"
        self.cpp_info.names["cmake_find_package_multi"] = "clickhouse-cpp-lib"
