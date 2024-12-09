import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.env import VirtualBuildEnv, VirtualRunEnv
from conan.tools.files import copy, get, rmdir, replace_in_file, mkdir
from conan.tools.scm import Version

required_conan_version = ">=2.1"

class OrcRecipe(ConanFile):
    name = "orc"
    description = "ORC is a self-describing type-aware columnar file format designed for Hadoop workloads"
    license = "Apache-2.0"
    homepage = "https://orc.apache.org/"
    url = "https://github.com/conan-io/conan-center-index"
    topics = ("orc", "columnar", "file-format", "hadoop")

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

    @property
    def _should_patch_thirdparty_toolchain(self):
        return self.version < "2.0.0"

    def export_sources(self):
        if self._should_patch_thirdparty_toolchain:
            copy(self, "ConanThirdpartyToolchain.cmake",
                 self.recipe_folder, os.path.join(self.export_sources_folder, "src", "cmake_modules"))

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if self.settings.compiler == "apple-clang":
            # AVX support is not enabled by default, might need to add -mavx512f to CXXFLAGS
            del self.options.build_avx512

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src", build_folder="build")

    def requirements(self):
        self.requires("protobuf/3.21.12")
        self.requires("lz4/1.9.4")
        self.requires("snappy/1.1.9")
        self.requires("zlib/[>=1.2.11 <2]")
        self.requires("zstd/[~1.5]")

    def validate(self):
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
        self._patch_sources()

    def generate(self):
        VirtualBuildEnv(self).generate()
        VirtualRunEnv(self).generate(scope="build")

        tc = CMakeToolchain(self)
        tc.variables["ORC_PACKAGE_KIND"] = "conan"
        tc.variables["BUILD_JAVA"] = False
        tc.variables["BUILD_CPP_TESTS"] = False
        tc.variables["BUILD_TOOLS"] = self.options.build_tools
        tc.variables["BUILD_LIBHDFSPP"] = False
        tc.variables["BUILD_POSITION_INDEPENDENT_LIB"] = bool(self.options.get_safe("fPIC", True))
        tc.variables["INSTALL_VENDORED_LIBS"] = False
        # AVX512 support is determined by ORC_USER_SIMD_LEVEL env var at runtime, defaults to off
        tc.variables["BUILD_ENABLE_AVX512"] = self.options.get_safe("build_avx512", False)
        tc.variables["STOP_BUILD_ON_WARNING"] = False
        tc.variables["CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS"] = True

        protoc_path = os.path.join(self.dependencies["protobuf"].cpp_info.bindir, "protoc")
        tc.variables["PROTOBUF_EXECUTABLE"] = protoc_path.replace("\\", "/")
        tc.variables["HAS_POST_2038"] = self.settings.os != "Windows"
        tc.variables["HAS_PRE_1970"] = self.settings.os != "Windows"
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def _patch_sources(self):
        if self._should_patch_thirdparty_toolchain:
            replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"),
                            "ThirdpartyToolchain", "ConanThirdpartyToolchain")
        # Allow shared builds
        replace_in_file(self, os.path.join(self.source_folder, "c++", "src", "CMakeLists.txt"),
                        "add_library (orc STATIC ${SOURCE_FILES})", "add_library (orc ${SOURCE_FILES})")

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        copy(self, "NOTICE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "share"))
        if self.settings.os == "Windows" and self.options.shared:
            mkdir(self, os.path.join(self.package_folder, "bin"))
            os.rename(os.path.join(self.package_folder, "lib", "orc.dll"),
                      os.path.join(self.package_folder, "bin", "orc.dll"))

    def package_info(self):
        self.cpp_info.libs = ["orc"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["pthread", "m"]
