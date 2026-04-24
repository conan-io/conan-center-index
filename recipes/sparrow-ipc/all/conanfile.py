from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build.cppstd import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rmdir
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version
import os

required_conan_version = ">=2.4"


class SparrowRecipe(ConanFile):
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

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def requirements(self):
        self.requires("sparrow/2.3.1", transitive_headers=True)
        self.requires("flatbuffers/24.12.23")
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

    def export_sources(self):
        export_conandata_patches(self)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        apply_conandata_patches(self)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["SPARROW_IPC_BUILD_SHARED"] = self.options.shared
        tc.generate()
        deps = CMakeDeps(self)
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
        postfix = "d" if self.settings.build_type == "Debug" else ""
        self.cpp_info.set_property("cmake_file_name", "sparrow-ipc")

        # Main sparrow-ipc component
        self.cpp_info.components["sparrow-ipc"].set_property("cmake_target_name", "sparrow-ipc::sparrow-ipc")
        self.cpp_info.components["sparrow-ipc"].libs = [f"sparrow-ipc{postfix}"]
        self.cpp_info.components["sparrow-ipc"].requires = ["sparrow::sparrow", "flatbuffers::libflatbuffers", "lz4::lz4", "zstd::zstdlib"]

        if not self.options.shared:
            self.cpp_info.components["sparrow-ipc"].defines.append("SPARROW_IPC_STATIC_LIB")

