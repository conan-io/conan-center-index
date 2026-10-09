from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build.cppstd import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps, cmake_layout
from conan.tools.files import copy, get, rmdir
from conan.tools.scm import Version
import os

required_conan_version = ">=2.4"


class SparrowIpcRecipe(ConanFile):
    name = "sparrow-ipc"
    description = "C++20 idiomatic APIs for the Apache Arrow Serialization and Interprocess Communication (IPC)"
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/sparrow-org/sparrow-ipc"
    topics = ("arrow", "apache arrow", "columnar format", "dataframe", "IPC")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"

    options = {
        "shared": [True, False],
        "fPIC": [True, False]
    }

    default_options = {
        "shared": False,
        "fPIC": True,
    }

    implements = ["auto_shared_fpic"]

    def requirements(self):
        # sparrow is part of the public interface of sparrow-ipc (sparrow::sparrow is PUBLIC in
        # upstream CMakeLists.txt), so consumers need both its headers and its libraries
        self.requires("sparrow/2.4.0", transitive_headers=True, transitive_libs=True)
        self.requires("flatbuffers/25.12.19")
        self.requires("lz4/1.9.4")
        self.requires("zstd/[>=1.5 <1.6]")

    @property
    def _compilers_minimum_version(self):
        # Upstream has these set as the minimum versions
        # regardless of cppstd support
        return {
            "apple-clang": "16",
            "clang": "18",
            "gcc": "11",
            "msvc": "194",
        }

    def validate(self):
        check_min_cppstd(self, 20)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler))
        if minimum_version and Version(self.settings.compiler.version) < Version(minimum_version):
            raise ConanInvalidConfiguration(f"{self.name} requires {self.settings.compiler} {minimum_version} or newer")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.28]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["SPARROW_IPC_BUILD_SHARED"] = self.options.shared
        tc.generate()
        deps = CMakeDeps(self)
        # Upstream CMakeLists.txt always links against `flatbuffers::flatbuffers`, but the
        # flatbuffers recipe names its target `flatbuffers::flatbuffers_shared` when it is
        # built as shared
        deps.set_property("flatbuffers", "cmake_target_name", "flatbuffers::flatbuffers")
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(
            self,
            "LICENSE",
            dst=os.path.join(self.package_folder, "licenses"),
            src=self.source_folder,
        )
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "share", "cmake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "sparrow-ipc")
        self.cpp_info.set_property("cmake_target_name", "sparrow-ipc::sparrow-ipc")
        self.cpp_info.libs = ["sparrow-ipc"]

        if not self.options.shared:
            self.cpp_info.defines.append("SPARROW_IPC_STATIC_LIB")
