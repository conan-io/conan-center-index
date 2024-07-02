from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd, stdcpp_library
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, replace_in_file, rm, rmdir, collect_libs
from conan.tools.microsoft import check_min_vs, is_msvc, is_msvc_static_runtime
from conan.tools.scm import Version, Git
import os

required_conan_version = ">=1.59.0"

class UpCppConan(ConanFile):
    name = "up-cpp"
    description = "C++ language implementation of a uProtocol language SDK"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/eclipse-uprotocol/up-cpp"
    topics = ("uprotocol", "sdv", "middleware")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    # TODO: Upon release of up-spec 1.5.8, this will need to be updated to:
    # proto_containing_folder = "up-spec"
    proto_containing_folder = "up-core-api"
    # TODO: Upon release of up-spec 1.5.8, this will need to be updated to:
    # proto_subfolder = "up-core-api"
    proto_subfolder = "."
    proto_folder = "uprotocol"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "build_testing": [True, False],
        "build_unbundled": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": False,
        "build_testing": False,
        "build_unbundled": False,
    }

    @property
    def _min_cppstd(self):
        return 14

    # unclear on what I should choose for msvc and Visual Studio
    @property
    def _compilers_minimum_version(self):
        return {
            "apple-clang": "13",
            "clang": "13",
            "gcc": "11",
            "msvc": "191",
            "Visual Studio": "15",
        }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")
        self.folders.build = os.path.join("build", str(self.settings.build_type))
        self.folders.install = "install"

    def build_requirements(self):
        self.build_requires("cmake/[>=3.18.0]")

    def requirements(self):
        self.requires("protobuf/3.21.12")
        self.requires("spdlog/1.13.0")
        if self.options.build_testing:
            self.requires("gtest/1.14.0")

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )
        if is_msvc(self):
            raise ConanInvalidConfiguration(
                f"{self.ref} need to have paths in CMake files updated to handle both \ and /."
            )
        if self.settings.compiler == "clang" and stdcpp_library(self) == "c++":
            raise ConanInvalidConfiguration(
                f"{self.ref} Experiencing some interference between math.h and the protobuf generated udiscovery.pb.h"
                  "when compiling with libc++ for some reason."
            )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

        # we clone protos from the appropriate repo at the appropriate tag to our local root to build
        rmdir(self, self.proto_containing_folder)

        git = Git(self)
        git_method = os.getenv("GIT_METHOD", "https")
        git.clone(self.conan_data["proto"][self.version][git_method], target=self.proto_containing_folder)
        git.folder=self.proto_containing_folder
        git.checkout(self.conan_data["proto"][self.version]["tag"])

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["PROTO_PATH"] = os.path.join(self.proto_containing_folder, os.path.join(self.proto_subfolder, self.proto_folder))
        tc.variables["BUILD_TESTING"] = self.options.build_testing
        tc.variables["BUILD_UNBUNDLED"] = self.options.build_unbundled
        tc.variables["BUILD_SHARED_LIBS"] = self.options.shared
        if is_msvc(self):
            tc.variables["USE_MSVC_RUNTIME_LIBRARY_DLL"] = not is_msvc_static_runtime(self)
        tc.generate()
        tc = CMakeDeps(self)
        tc.generate()
        tc = VirtualBuildEnv(self)
        tc.generate(scope="build")

    def _patch_sources(self):
        apply_conandata_patches(self)

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        rm(self, "*.la", os.path.join(self.package_folder, "lib"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "lib"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "bin"))

    def package_info(self):
        self.cpp_info.libs = ["up-cpp"]

        self.cpp_info.set_property("cmake_file_name", "up-cpp")
        self.cpp_info.set_property("cmake_target_name", "up-cpp::up-cpp")
        self.cpp_info.set_property("pkg_config_name", "up-cpp")
        self.cpp_info.libs = collect_libs(self)

        self.cpp_info.set_property("cmake_target_name", "up-cpp::up-cpp")
        self.cpp_info.requires = ["spdlog::spdlog", "protobuf::protobuf"]

        self.cpp_info.names["cmake_find_package"] = "up-cpp"
        self.cpp_info.names["cmake_find_package_multi"] = "up-cpp"
