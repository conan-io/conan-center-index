from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps, cmake_layout
from conan.tools.files import copy, get, rmdir, apply_conandata_patches, export_conandata_patches
from conan.tools.scm import Version
from conan.errors import ConanInvalidConfiguration
import os


class NodesoupConan(ConanFile):
    name = "nodesoup"
    description = "Force-directed graph layout with Fruchterman-Reingold"
    license = "MIT",
    topics = ("graph", "visualization", "layout", "kamada", "kawai", "fruchterman", "reingold")
    homepage = "https://github.com/olvb/nodesoup"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "arch", "compiler", "build_type"
    package_type = "library"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    def layout(self):
        cmake_layout(self, src_folder="src")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    @property
    def _min_cppstd(self):
        return 14

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)
        if self.settings.compiler == "clang":
            if Version(self.settings.compiler.version) < "5.0" and self.settings.compiler.libcxx in ("libstdc++", "libstdc++11"):
                raise ConanInvalidConfiguration("The version of libstdc++(11) of the current compiler does not support building nodesoup")

    def export_sources(self):
        export_conandata_patches(self)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_DEMO"] = False
        tc.variables["CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS"] = True
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.includedirs.append(os.path.join("include", "nodesoup"))
        self.cpp_info.libs = ["nodesoup"]
        self.cpp_info.names["cmake_find_package"] = "nodesoup"
        self.cpp_info.names["cmake_find_package_multi"] = "nodesoup"
