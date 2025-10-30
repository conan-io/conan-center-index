from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, export_conandata_patches, get, replace_in_file
from conan.tools.microsoft import is_msvc_static_runtime
from conan.tools.scm import Version
import os

required_conan_version = ">=2.4"


class DoxygenConan(ConanFile):
    name = "doxygen"
    description = "A documentation system for C++, C, Java, IDL and PHP --- Note: Dot is disabled in this package"
    topics = ("installer", "devtool", "documentation")
    homepage = "https://github.com/doxygen/doxygen"
    license = "GPL-2.0-or-later"
    url = "https://github.com/conan-io/conan-center-index"
    package_type = "application"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "enable_parse": [True, False],
        "enable_search": [True, False],
        "enable_app": [True, False],
    }
    default_options = {
        "enable_parse": True,
        "enable_search": True,
        "enable_app": False
    }

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if self.options.enable_search:
            self.requires("xapian-core/1.4.19")
            self.requires("zlib/[>=1.2.11 <2]")
        if self.options.enable_app or self.options.enable_parse:
            self.requires("libiconv/1.17")

    def validate_build(self):
        if (self.settings.compiler == "apple-clang" and Version(self.settings.compiler.version) >= "17") or \
           (self.settings.compiler == "clang" and Version(self.settings.compiler.version) >= "19"):
            check_min_cppstd(self, "20")
        else:
            check_min_cppstd(self, "17")

    def validate(self):
        if self.settings.compiler == "gcc" and Version(self.settings.compiler.version) < "5":
            raise ConanInvalidConfiguration("Doxygen requires GCC >=5")

        if self.settings.compiler == "msvc" and Version(self.settings.compiler.version) < "191":
            raise ConanInvalidConfiguration("Doxygen requires Visual Studio 2017 or newer")

    def build_requirements(self):
        if self.settings_build.os == "Windows":
            self.tool_requires("winflexbison/2.5.24")
        else:
            self.tool_requires("flex/2.6.4")
            self.tool_requires("bison/3.8.2")

        self.tool_requires("cmake/[>=3.19 <4]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

        #Do not build manpages
        cmakelists = os.path.join(self.source_folder, "CMakeLists.txt")
        replace_in_file(self, cmakelists, "add_subdirectory(doc)", "")
        replace_in_file(self, cmakelists, "set(CMAKE_CXX_STANDARD", "##set(CMAKE_CXX_STANDARD")

        if Version(self.version) == "1.15.0":
            # https://github.com/doxygen/doxygen/issues/11833
            replace_in_file(self, cmakelists, "MACOS_VERSION_MIN 10.14", "MACOS_VERSION_MIN 10.15")

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["build_parse"] = self.options.enable_parse
        tc.variables["build_search"] = self.options.enable_search
        tc.variables["build_app"] = self.options.enable_app
        tc.variables["use_libc++"] = self.settings.compiler.get_safe("libcxx") == "libc++"
        tc.variables["win_static"] = is_msvc_static_runtime(self)
        tc.generate()

        deps = CMakeDeps(self)
        deps.set_property("libiconv", "cmake_additional_variables_prefixes", ["ICONV"])
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.set_property("cmake_find_mode", "none")
        self.cpp_info.libdirs = []
        self.cpp_info.includedirs = []
