import os

from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.files import get, rmdir, copy
from conan.tools.cmake import CMake, cmake_layout


class arg_routerRecipe(ConanFile):
    name = "arg_router"
    license = "BSL-1.0"
    homepage = "https://github.com/cmannett85/arg_router"
    url = "https://github.com/conan-io/conan-center-index"
    description = "C++ command line argument parsing and routing."
    topics = ("cpp", "command-line", "argument-parser", "header-only")

    # CMake >= 3.18 is required https://github.com/cmannett85/arg_router/blob/449567723d6c0e9db0a4c89277066c9a53b299fa/CMakeLists.txt#L5
    tool_requires = "cmake/3.25.3"
    requires = "boost/1.81.0", "span-lite/0.10.3"

    settings = "os", "arch", "compiler", "build_type"
    package_type = "header-library"
    generators = "CMakeDeps", "CMakeToolchain"
    no_copy_source = True

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, 17)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def build(self):
        cmake = CMake(self)
        cmake.configure(variables={"INSTALLATION_ONLY": True})
        cmake.build()

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        # Folders not used for header-only
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []

        self.cpp_info.set_property("cmake_file_name", "arg_router")
        self.cpp_info.set_property("cmake_target_name", "arg_router::arg_router")

    def package_id(self):
        # build_type and compiler are needed for the Conan's CMake tools but are not actually used
        self.info.clear()
