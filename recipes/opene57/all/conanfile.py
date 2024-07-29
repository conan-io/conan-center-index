import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, export_conandata_patches, get, replace_in_file
from conan.tools.microsoft import is_msvc, is_msvc_static_runtime
from conan.tools.scm import Version

required_conan_version = ">=1.54.0"


class Opene57Conan(ConanFile):
    name = "opene57"
    description = "A C++ library for reading and writing E57 files, a fork of the original libE57 (http://libe57.org)"
    license = ("MIT", "BSL-1.0")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/openE57/openE57"
    topics = ("e57", "libe57", "3d", "astm")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_tools": [True, False],
        "with_docs":  [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_tools": False,
        "with_docs":  False
    }

    @property
    def _min_cppstd(self):
        return "17"

    @property
    def _minimum_compilers_version(self):
        return {
            "Visual Studio": "15",
            "msvc": "191",
            "gcc": "7",
            "clang": "6",
            "apple-clang": "10",
        }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        if self.options.with_tools:
            self.options["boost"].multithreading = True

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if self.options.with_tools:
            self.requires("boost/1.84.0")

        if self.options.with_docs:
            self.requires("doxygen/1.9.4")

        if self.settings.os != "Windows":
            self.requires("icu/74.1")

        self.requires("xerces-c/3.2.4")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)

        minimum_version = self._minimum_compilers_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["PROJECT_VERSION"] = self.version
        tc.variables["BUILD_EXAMPLES"] = False
        tc.variables["BUILD_TOOLS"] = self.options.with_tools
        tc.variables["BUILD_TESTS"] = False
        tc.variables["BUILD_DOCS"] = self.options.with_docs

        if is_msvc(self):
            tc.variables["BUILD_WITH_MT"] = is_msvc_static_runtime(self)
        tc.variables["CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS"] = self.options.shared
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def _patch_sources(self):
        # Do not raise an error for shared builds
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"), "message(FATAL_ERROR", "# ")
        compiler_opts = os.path.join(self.source_folder, "src", "cmake", "compiler_options.cmake")
        # Disable ASan and UBSan as these require linking against asan and ubsan runtime libraries
        # FIXME: Figure out how to link against these using Conan
        replace_in_file(self, compiler_opts, "$<$<CONFIG:DEBUG>:-fsanitize=address>", "")
        replace_in_file(self, compiler_opts, "$<$<CONFIG:DEBUG>:-fsanitize=undefined>", "")
        if self.settings.compiler == "apple-clang":
            replace_in_file(self, compiler_opts, "$<$<CONFIG:DEBUG>:-fsanitize=leak>", "")
        if self.settings.compiler == "gcc" and Version(self.settings.compiler.version) < "8":
            replace_in_file(self, compiler_opts, "-fstack-clash-protection", "")

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        copy(self, "LICENSE.libE57", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()
        os.remove(os.path.join(self.package_folder, "CHANGELOG.md"))

    def package_info(self):
        lib_suffix = "-d" if self.settings.build_type == "Debug" else ""
        self.cpp_info.libs = [f"openE57{lib_suffix}", f"openE57las{lib_suffix}"]

        self.cpp_info.defines.append(f"E57_REFIMPL_REVISION_ID={self.name}-{self.version}")
        self.cpp_info.defines.append("XERCES_STATIC_LIBRARY")
        self.cpp_info.defines.append("CRCPP_INCLUDE_ESOTERIC_CRC_DEFINITIONS")
        self.cpp_info.defines.append("CRCPP_USE_CPP11")

        # TODO: to remove in conan v2
        if self.options.with_tools:
            bin_path = os.path.join(self.package_folder, "bin")
            self.env_info.PATH.append(bin_path)
