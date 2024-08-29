import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout, CMakeDeps
from conan.tools.files import get, rm, rmdir, copy, replace_in_file
from conan.tools.scm import Version

required_conan_version = ">=1.54.0"


class yomm2Recipe(ConanFile):
    name = "yomm2"
    package_type = "header-library"
    # Optional metadata
    license = "BSL-1.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/jll63/yomm2"
    description = "Fast, orthogonal, open multi-methods. Solve the Expression Problem in C++17"
    topics = ("multi-methods", "multiple-dispatch", "open-methods", "shared-library",
              "header-only", "polymorphism", "expression-problem", "c++17")
    # Binary configuration
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "header_only": [True, False],
    }
    default_options = {
        "header_only": True
    }

    @property
    def _min_cppstd(self):
        return 17

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "8",
            "clang": "5",
            "apple-clang": "13",
            "msvc": "192"
        }

    def configure(self):
        if not bool(self.options.header_only):
            self.package_type = "shared-library"

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )
        if self.settings.compiler == "apple-clang" and not bool(self.options.header_only):
            raise ConanInvalidConfiguration(
                f"{self.ref} dynamic library builds are not supported on MacOS."
            )

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.20 <4]")

    def requirements(self):
        # Upstream requires Boost 1.74
        # Using more modern Boost version to avoid issues like the one commented here:
        # - https://github.com/conan-io/conan/issues/15977#issuecomment-2098003085
        self.requires("boost/1.85.0", transitive_headers=True)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def generate(self):
        deps = CMakeDeps(self)
        deps.generate()
        tc = CMakeToolchain(self)
        tc.variables["YOMM2_ENABLE_EXAMPLES"] = "OFF"
        tc.variables["YOMM2_ENABLE_TESTS"] = "OFF"
        tc.variables["YOMM2_SHARED"] = not bool(self.options.header_only)
        tc.generate()

    def _patch_sources(self):
        if Version(self.version) <= "1.5.1":
            cmakelists = os.path.join(self.source_folder, "CMakeLists.txt")
            replace_in_file(self, cmakelists, "add_subdirectory(docs.in)", "")

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package_id(self):
        # if yomm2 is built as static, it behaves as a header-only one
        if self.info.options.header_only:
            self.info.clear()

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rm(self, "*.pdb", os.path.join(self.package_folder, "bin"))
        if self.options.header_only:
            rmdir(self, os.path.join(self.package_folder, "lib"))
        else:
            rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "YOMM2")
        self.cpp_info.set_property("cmake_target_name", "YOMM2::yomm2")
        if self.options.header_only:
            self.cpp_info.bindirs = []
            self.cpp_info.libdirs = []
        else:  # shared-library
            self.cpp_info.libs = ["yomm2"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")
