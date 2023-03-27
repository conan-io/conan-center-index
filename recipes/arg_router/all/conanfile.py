import os

from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.files import get, rmdir
from conan.tools.cmake import CMakeDeps, CMakeToolchain, CMake


class arg_routerRecipe(ConanFile):
    name = "arg_router"
    license = "BSL-1.0"
    author = "Camden Mannett"
    url = "https://github.com/cmannett85/arg_router"
    description = "C++ command line argument parsing and routing."
    topics = ("cpp", "command-line", "argument-parser", "header-only")

    requires = "boost/1.74.0", "span-lite/0.10.3"

    settings = "build_type", "compiler"
    default_options = {"boost/*:header_only": True}
    package_type = "header-library"
    generators = "CMakeDeps", "CMakeToolchain"
    no_copy_source = True

    def validate(self):
        check_min_cppstd(self, 17)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def layout(self):
        self.folders.build = "."
        self.folders.generators = "."
        self.cpp.source.includedirs = ["include"]

    def build(self):
        cmake = CMake(self)
        cmake.configure(variables={"INSTALLATION_ONLY": True})
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()

        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        # Folders not used for header-only
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []

        self.cpp_info.set_property("cmake_file_name", "arg_router")
        self.cpp_info.set_property(
            "cmake_target_name", "arg_router::arg_router")

    def package_id(self):
        # build_type and compiler are needed for the Conan's CMake tools but are not actually used
        self.info.settings.clear()
