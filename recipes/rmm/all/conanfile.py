import os

from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import export_conandata_patches, get, copy, replace_in_file

required_conan_version = ">=1.52.0"


class RmmConan(ConanFile):
    name = "rmm"
    description = "RAPIDS Memory Manager"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/rapidsai/rmm"
    topics = ("cuda", "memory-management", "memory-allocation", "rapids", "header-only")
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"

    @property
    def _min_cppstd(self):
        return 17

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("thrust/1.17.2", transitive_headers=True, transitive_libs=True)
        self.requires("spdlog/1.11.0", transitive_headers=True, transitive_libs=True)
        self.requires("fmt/9.1.0", transitive_headers=True, transitive_libs=True)

    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_TESTS"] = False
        tc.variables["BUILD_BENCHMARKS"] = False
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def _patch_sources(self):
        for pattern, repl in [
            ("include(rapids-cpm)", ""),
            ("rapids_cpm_init()", ""),
            ("include(cmake/thirdparty", "# include(cmake/thirdparty"),
        ]:
            replace_in_file(
                self,
                os.path.join(self.source_folder, "CMakeLists.txt"),
                pattern,
                repl,
            )

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(
            self,
            pattern="LICENSE",
            dst=os.path.join(self.package_folder, "licenses"),
            src=self.source_folder,
        )
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
