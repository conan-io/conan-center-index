from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps, cmake_layout
from conan.tools.files import get, copy, rmdir
from conan.tools.build import check_min_cppstd
from conan.tools.microsoft import is_msvc
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=2.1"


class OmplConan(ConanFile):
    name = "ompl"
    description = "The Open Motion Planning Library (OMPL)"
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://ompl.kavrakilab.org/"
    topics = ("motion-planning", "robotics", "path-planning")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    implements = ["auto_shared_fpic"]

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("eigen/[>=3.4.0 <4]", transitive_headers=True)
        self.requires("boost/1.88.0", transitive_headers=True)

    def validate(self):
        check_min_cppstd(self, 17)
        if is_msvc(self) and self.options.shared:
            # INFO https://github.com/ompl/ompl/blob/1.7.0/src/ompl/CMakeLists.txt#L36
            raise ConanInvalidConfiguration('Only static library is provided for MSVC compiler. Use -o "ompl/*:shared=False"')
        elif not is_msvc(self) and not self.options.shared:
            raise ConanInvalidConfiguration('Only shared library is provided for non-MSVC compilers. Use -o "ompl/*:shared=True"')

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["OMPL_BUILD_PYBINDINGS"] = False
        tc.cache_variables["OMPL_BUILD_DEMOS"] = False
        tc.cache_variables["OMPL_BUILD_TESTS"] = False
        tc.cache_variables["OMPL_BUILD_PYTESTS"] = False
        tc.cache_variables["OMPL_REGISTRATION"] = False
        tc.cache_variables["OMPL_VERSIONED_INSTALL"] = False
        tc.cache_variables["CMAKE_DISABLE_FIND_PACKAGE_castxml"] = True
        tc.cache_variables["CMAKE_DISABLE_FIND_PACKAGE_Doxygen"] = True
        tc.cache_variables["CMAKE_DISABLE_FIND_PACKAGE_spot"] = True
        tc.cache_variables["CMAKE_DISABLE_FIND_PACKAGE_Triangle"] = True
        tc.cache_variables["CMAKE_DISABLE_FIND_PACKAGE_flann"] = True
        tc.generate()

        cd = CMakeDeps(self)
        cd.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.libs = ["ompl"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["m", "pthread"]
