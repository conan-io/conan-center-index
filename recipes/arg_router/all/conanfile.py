import os

from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.files import get, rmdir
from conan.tools.cmake import CMake, cmake_layout


class arg_routerRecipe(ConanFile):
    name = "arg_router"
    license = "BSL-1.0"
    homepage = "https://github.com/cmannett85/arg_router"
    url = "https://github.com/conan-io/conan-center-index"
    description = "C++ command line argument parsing and routing."
    topics = ("cpp", "command-line", "argument-parser", "header-only")

    # CMake >= 3.18 is required but the recipe for it is not compatible with Conan v2, so just use
    # the latest at the time of writing
    tool_requires = "cmake/3.25.3"
    requires = "boost/1.74.0", "span-lite/0.10.3"

    settings = "os", "arch", "compiler", "build_type"
    default_options = {"boost/*:header_only": True}
    package_type = "header-library"
    generators = "CMakeDeps", "CMakeToolchain"
    no_copy_source = True

    def validate(self):
        check_min_cppstd(self, 17)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def layout(self):
        cmake_layout(self)

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
        self.info.clear()
