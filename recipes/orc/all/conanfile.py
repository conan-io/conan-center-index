import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import copy, get, rmdir, save, replace_in_file
from conan.tools.scm import Version

required_conan_version = ">=1.60.0 <2.0 || >=2.0.5"

class OrcConan(ConanFile):
    name = "orc"
    description = "ORC is a self-describing type-aware columnar file format designed for Hadoop workloads"
    license = "Apache-2.0"
    homepage = "https://orc.apache.org/"
    url = "https://github.com/conan-io/conan-center-index"
    topics = ("columnar", "file-format", "hadoop")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "build_tools": [True, False],
        "build_avx512": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "build_tools": False,
        "build_avx512": True,
    }

    @property
    def _min_cppstd(self):
        return 17

    @property
    def _compilers_minimum_version(self):
        return {
            "Visual Studio": "16",
            "msvc": "192",
            "gcc": "8",
            "clang": "7",
            "apple-clang": "12",
        }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        # FIXME? not sure why transitive_libs=True is necessary here.
        # None of these are not used in the public headers.
        self.requires("protobuf/3.21.12", transitive_libs=True)
        self.requires("lz4/1.9.4", transitive_libs=True)
        self.requires("snappy/1.1.10", transitive_libs=True)
        self.requires("zlib/[>=1.2.11 <2]", transitive_libs=True)
        self.requires("zstd/1.5.5", transitive_libs=True)

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )

    def build_requirements(self):
        self.tool_requires("protobuf/<host_version>")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    @property
    def _unvendored_packages(self):
        return ["LZ4", "ZSTD", "Protobuf", "Snappy", "ZLIB"]

    def generate(self):
        venv = VirtualBuildEnv(self)
        venv.generate()

        tc = CMakeToolchain(self)
        tc.cache_variables["BUILD_CPP_TESTS"] = False
        tc.cache_variables["BUILD_JAVA"] = False
        tc.cache_variables["BUILD_LIBHDFSPP"] = False
        tc.cache_variables["BUILD_TOOLS"] = self.options.build_tools
        tc.cache_variables["ENABLE_TEST"] = False
        tc.cache_variables["HAS_POST_2038"] = self.settings.os != "Windows"
        tc.cache_variables["HAS_PRE_1970"] = self.settings.os != "Windows"
        tc.cache_variables["INSTALL_VENDORED_LIBS"] = False
        tc.cache_variables["STOP_BUILD_ON_WARNING"] = False
        # AVX512 support is determined by ORC_USER_SIMD_LEVEL env var at runtime, defaults to off
        tc.cache_variables["BUILD_ENABLE_AVX512"] = self.options.build_avx512
        protoc_path = os.path.join(self.dependencies["protobuf"].package_folder, "bin", "protoc")
        tc.cache_variables["PROTOBUF_EXECUTABLE"] = protoc_path.replace("\\", "/")
        tc.variables["CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS"] = True
        tc.generate()

        deps = CMakeDeps(self)
        for pkg in self._unvendored_packages:
            deps.set_property(pkg.lower(), "cmake_target_name", f"orc::{pkg.lower()}")
        deps.generate()

    def _patch_sources(self):
        # Unvendor packages
        for pkg in self._unvendored_packages:
            os.unlink(os.path.join(self.source_folder, "cmake_modules", f"Find{pkg}.cmake"))
        save(self, os.path.join(self.source_folder, "cmake_modules", "ThirdpartyToolchain.cmake"),
             "\n".join(f"find_package({pkg} REQUIRED CONFIG)" for pkg in self._unvendored_packages))
        # Allow shared builds
        replace_in_file(self, os.path.join(self.source_folder, "c++", "src", "CMakeLists.txt"),
                        "add_library (orc STATIC ${SOURCE_FILES})", "add_library (orc ${SOURCE_FILES})")

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.libs = ["orc"]
