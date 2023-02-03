from conan import ConanFile
from conan.tools.files import rmdir, rm, copy, get, collect_libs
from conan.tools.build import check_min_cppstd
from conan.tools.scm import Version
from conan.tools.layout import cmake_layout
from conan.tools.microsoft import check_min_vs, is_msvc
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain
import os

required_conan_version = ">=1.50.0"

class EdynConan(ConanFile):
    name = "edyn"
    description = "Edyn is a real-time physics engine organized as an ECS"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/xissburg/edyn"
    topics = ("physics", "game-development", "ecs")
    settings = "os", "arch", "compiler", "build_type"

    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "floating_type": ["float", "double"],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "floating_type": "float",
    }

    @property
    def _compiler_required(self):
        return {
            "gcc": "9.3", # GCC 9.3 started supporting attributes in constructor arguments
            "clang": "8",
            "apple-clang": "10",
        }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("entt/3.10.1")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, 17)
        check_min_vs(self, 192)
        if not is_msvc(self):
            try:
                minimum_required_compiler_version = self._compiler_required[str(self.settings.compiler)]
                if Version(self.settings.compiler.version) < minimum_required_compiler_version:
                    raise ConanInvalidConfiguration("This package requires C++17 support. The current compiler does not support it.")
            except KeyError:
                self.output.warn("This recipe has no support for the current compiler. Please consider adding it.")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["EDYN_INSTALL"] = True
        tc.variables["EDYN_BUILD_EXAMPLES"] = False
        if self.options.floating_type == "double":
            tc.variables["EDYN_CONFIG_DOUBLE"] = True
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()

        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        rm(self, pattern="*.pdb", folder=self.package_folder, recursive=True)

    def package_info(self):
        self.cpp_info.libs = collect_libs(self)

        self.cpp_info.set_property("cmake_file_name", "Edyn")
        self.cpp_info.set_property("cmake_target_name", "Edyn::Edyn")
        self.cpp_info.set_property("pkg_config_name", "Edyn")

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs += ["m", "pthread"]
        elif self.settings.os == "Windows":
            self.cpp_info.system_libs = ["winmm"]

        #  TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "Edyn"
        self.cpp_info.filenames["cmake_find_package_multi"] = "Edyn"
        self.cpp_info.names["cmake_find_package"] = "Edyn"
        self.cpp_info.names["cmake_find_package_multi"] = "Edyn"
