import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd, valid_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir, replace_in_file, export_conandata_patches, apply_conandata_patches
from conan.tools.microsoft import is_msvc

required_conan_version = ">=1.52.0"


class LibunifexConan(ConanFile):
    name = "libunifex"
    description = "A prototype implementation of the C++ sender/receiver async programming model"
    license = ("Apache-2.0", "LLVM-exception")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/facebookexperimental/libunifex"
    topics = ("async", "cpp")

    package_type = "static-library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "fPIC": [True, False],
        "with_liburing": [True, False],
    }
    default_options = {
        "fPIC": True,
        "with_liburing": False,  # Enabled by default in the project, but incompatible with the Linux version used in C3I
    }

    @property
    def _minimum_standard(self):
        if is_msvc(self):
            # Otherwise a forward declaration `extern const _schedule::_fn schedule;`
            # conflicts with the implementation `inline constexpr _schedule::_fn schedule {};`
            # https://github.com/facebookexperimental/libunifex/issues/591
            return 20
        return 17

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "9",
            "clang": "10",
            "apple-clang": "11",
            "Visual Studio": "17",
            "msvc": "193",
        }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if not self.settings.os == "Linux":
            del self.options.with_liburing

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if self.options.get_safe("with_liburing"):
            self.requires("liburing/2.4", transitive_headers=True, transitive_libs=True)

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._minimum_standard)

        def lazy_lt_semver(v1, v2):
            return all(int(p1) < int(p2) for p1, p2 in zip(str(v1).split("."), str(v2).split(".")))

        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and lazy_lt_semver(self.settings.compiler.version, minimum_version):
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._minimum_standard}, which your compiler does not support."
            )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_TESTING"] = False
        tc.variables["UNIFEX_BUILD_EXAMPLES"] = False
        tc.variables["UNIFEX_NO_LIBURING"] = not self.options.get_safe("with_liburing", False)
        if not valid_min_cppstd(self, self._minimum_standard):
            tc.variables["CMAKE_CXX_STANDARD"] = self._minimum_standard
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0077"] = "NEW"
        tc.generate()
        deps = CMakeDeps(self)
        deps.set_property("liburing", "cmake_file_name", "LIBURING")
        deps.generate()

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def _patch_sources(self):
        apply_conandata_patches(self)
        # Ensure liburing from the system is not used and that uuper-case variables are generated
        required = "REQUIRED" if self.settings.os == "Linux" else ""
        replace_in_file(self, os.path.join(self.source_folder, "cmake", "unifex_flags.cmake"),
                        "find_package(LibUring COMPONENTS)",
                        f"find_package(LIBURING {required} CONFIG NO_DEFAULT_PATH PATHS ${{CMAKE_PREFIX_PATH}})")
        replace_in_file(self, os.path.join(self.source_folder, "cmake", "unifex_env.cmake"), "-Werror", "")
        replace_in_file(self, os.path.join(self.source_folder, "cmake", "unifex_env.cmake"), "/WX", "")
        # Allow cppstd to be overridden
        replace_in_file(self, os.path.join(self.source_folder, "source", "CMakeLists.txt"),
                        "target_compile_features(unifex PUBLIC cxx_std_17)", "")

    def package(self):
        copy(self, "LICENSE.txt",
             dst=os.path.join(self.package_folder, "licenses"),
             src=self.source_folder)
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []

        self.cpp_info.set_property("cmake_file_name", "unifex")
        self.cpp_info.set_property("cmake_target_name", "unifex::unifex")
        self.cpp_info.set_property("pkg_config_name", "unifex")

        self.cpp_info.components["unifex"].libs = ["unifex"]
        self.cpp_info.components["unifex"].set_property("cmake_target_name", "unifex::unifex")
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["unifex"].system_libs = ["pthread"]
        if self.options.get_safe("with_liburing"):
            self.cpp_info.components["unifex"].requires.append("liburing::liburing")

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.names["cmake_find_package"] = "unifex"
        self.cpp_info.names["cmake_find_package_multi"] = "unifex"
        self.cpp_info.components["unifex"].names["cmake_find_package"] = "unifex"
        self.cpp_info.components["unifex"].names["cmake_find_package_multi"] = "unifex"
