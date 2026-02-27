from conan import ConanFile
from conan.tools.apple import is_apple_os
from conan.tools.build import check_min_cppstd, cross_building
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, replace_in_file, rmdir
from os.path import join

required_conan_version = ">=1.53.0"


class OGDFConan(ConanFile):
    name = "ogdf"
    description = "Open Graph algorithms and Data structures Framework"
    license = ("GPL-2.0-or-later", "GPL-3.0-or-later")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://ogdf.net"
    topics = ("graph", "algorithm", "data-structures")
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    @property
    def _min_cppstd(self):
        return 17

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)
        if cross_building(self) and is_apple_os(self):
            # FIXME: https://github.com/ogdf/ogdf/issues/214
            # error: unknown target CPU 'apple-m2'
            raise ConanInvalidConfiguration("Cross-building is not support on Mac yet. See https://github.com/ogdf/ogdf/issues/214.")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def requirements(self):
        self.requires("coin-clp/1.17.7")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["COIN_SOLVER"] = "CLP"
        tc.variables["COIN_SOLVER_IS_EXTERNAL"] = 0
        tc.generate()
        tc = CMakeDeps(self)
        tc.generate()

    def _patch_sources(self):
        # delete code from other cci packages
        rmdir(self, join(self.source_folder, "src", "coin"))
        rmdir(self, join(self.source_folder, "include", "coin"))
        rmdir(self, join(self.source_folder, "include", "ogdf", "lib", "backward"))
        # do not set C++ standard
        replace_in_file(self, join(self.source_folder, "CMakeLists.txt"), "set(CMAKE_CXX_STANDARD ", "## set(CMAKE_CXX_STANDARD ")
        # use cci packages where available
        replace_in_file(self, join(self.source_folder, "CMakeLists.txt"), "include(coin)", "find_package(coin-clp REQUIRED CONFIG)")
        replace_in_file(self, join(self.source_folder, "cmake", "ogdf.cmake"), "target_link_libraries(OGDF PUBLIC COIN)", "target_link_libraries(OGDF PUBLIC coin-clp::coin-clp)")

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build(target="OGDF")

    def package(self):
        cmake = CMake(self)
        cmake.install()
        copy(self, pattern="*.h", src=join(self.package_folder, "include", "ogdf-release", "ogdf"), dst=join(self.package_folder, "include", "ogdf"))
        rmdir(self, join(self.package_folder, "include", "ogdf-release"))
        copy(self, pattern="*.h", src=join(self.package_folder, "include", "ogdf-debug", "ogdf"), dst=join(self.package_folder, "include", "ogdf"))
        rmdir(self, join(self.package_folder, "include", "ogdf-debug"))

    def package_info(self):
        self.cpp_info.libs = ["OGDF"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")
            self.cpp_info.system_libs.append("pthread")
