import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, replace_in_file
from conan.tools.microsoft import is_msvc, is_msvc_static_runtime
from conan.tools.scm import Version

required_conan_version = ">=2.1"


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
        "with_docs":  [True, False],
        "xml_backend": ["xerces", "libxml2", "pugixml"]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_tools": False,
        "with_docs": False,
        "xml_backend": "xerces"
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
    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if self.options.with_docs:
            self.requires("doxygen/[>=1.8 <2]")

        if self.options.xml_backend == "xerces":
            self.requires("xerces-c/3.3.0")
            if self.settings.os != "Windows":
                self.requires("icu/78.2")
        elif self.options.xml_backend == "libxml2":
            self.requires("libxml2/2.15.3")
        else:
            self.requires("pugixml/1.15")

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
        tc.cache_variables["E57_XML_BACKEND"] = self.options.xml_backend

        if is_msvc(self):
            tc.variables["BUILD_WITH_MT"] = is_msvc_static_runtime(self)
        tc.variables["CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS"] = self.options.shared
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def _patch_sources(self):
        # Do not raise an error for shared builds
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"), "message(FATAL_ERROR", "# ")
        # Disable clang-format auto execution which fails in Windows
        replace_in_file(
            self,
            os.path.join(self.source_folder, "src", "cmake", "clang_format.cmake"),
            "function(target_clangformat_setup target)",
            "function(target_clangformat_setup target)\nreturn()",
        )
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
