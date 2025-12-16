from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rm, rmdir, replace_in_file
import os


required_conan_version = ">=2.0.9"


class VerilogSlangConan(ConanFile):
    name = "verilog-slang"
    description = "SystemVerilog compiler and language services"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://sv-lang.com/"
    topics = ("parse", "compiler", "verilog", "language-service", "systemverilog")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }
    implements = ["auto_shared_fpic"]

    def layout(self):
        cmake_layout(self, src_folder="src")

    def validate(self):
        check_min_cppstd(self, 20)

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.20]")

    def requirements(self):
        self.requires("fmt/12.1.0")
        if not self.options.shared or not self.settings.os == "Windows":
            self.requires("mimalloc/2.2.4")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        # INFO: Let Conan handle the C++ standard by settings.compiler.cppstd
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"),
                        "set(CMAKE_CXX_STANDARD",
                        "# set(CMAKE_CXX_STANDARD")

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["SLANG_INCLUDE_TESTS"] = False
        tc.cache_variables["SLANG_INCLUDE_TOOLS"] = False
        if self.settings.os == "Windows" and self.options.shared:
            # INFO: Make Error at external/CMakeLists.txt:74 (message):
            #  mimalloc cannot be used with Windows shared lib builds
            tc.cache_variables["SLANG_USE_MIMALLOC"] = False
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        copy(self, "*", os.path.join(self.source_folder, "LICENSES"), os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        rm(self, "*.pdb", self.package_folder, recursive=True)

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "sv-lang")
        self.cpp_info.set_property("cmake_file_name", "slang")

        self.cpp_info.components["boost_unordered"].set_property("cmake_target_name", "slang::boost_unordered")
        self.cpp_info.components["boost_unordered"].defines = ["SLANG_BOOST_SINGLE_HEADER"]
        self.cpp_info.components["boost_unordered"].libdirs = []

        self.cpp_info.components["core"].set_property("cmake_target_name", "slang::slang")
        self.cpp_info.components["core"].requires = ["fmt::fmt", "boost_unordered"]
        self.cpp_info.components["core"].defines = ["SLANG_USE_THREADS"]
        if self.settings.build_type == "Debug":
            self.cpp_info.components["core"].defines.append("SLANG_DEBUG")
        if not self.options.shared:
            self.cpp_info.components["core"].defines.append("SLANG_STATIC_DEFINE")
        if not self.options.shared or not self.settings.os == "Windows":
            self.cpp_info.components["core"].requires.append("mimalloc::mimalloc")
            self.cpp_info.components["core"].defines.append("SLANG_USE_MIMALLOC")
        self.cpp_info.components["core"].libs = ["svlang"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["core"].system_libs = ["m", "pthread", "dl"]
