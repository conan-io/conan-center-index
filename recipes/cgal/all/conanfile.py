import os
import textwrap
from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import get, replace_in_file, rmdir, rm, copy, save, export_conandata_patches, patch
from conan.tools.build import check_min_cppstd
from conan.tools.scm import Version
from conan.errors import ConanInvalidConfiguration

required_conan_version = ">=1.50.0"

class CgalConan(ConanFile):
    name = "cgal"
    license = "GPL-3.0-or-later", "LGPL-3.0-or-later"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/CGAL/cgal"
    description = "C++ library that provides easy access to efficient and reliable algorithms"\
                  " in computational geometry."
    topics = ("cgal", "geometry", "algorithms")
    settings = "os", "compiler", "build_type", "arch"
    generators = "CMakeDeps"
    short_paths = True

    @property
    def _min_cppstd(self):
        return "14"

    @property
    def _minimum_compilers_version(self):
        return {
            "Visual Studio": "15",
            "msvc": "191",
            "gcc": "5",
            "clang": "5",
            "apple-clang": "5.1",
        }

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("boost/1.78.0")
        self.requires("eigen/3.4.0")
        self.requires("mpfr/4.1.0")

    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._minimum_compilers_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support.",
            )

    def _patch_sources(self):
        replace_in_file(self,  os.path.join(self.source_folder, "CMakeLists.txt"),
                        "if(NOT PROJECT_NAME)", "if(1)", strict=False)
        for it in self.conan_data.get("patches", {}).get(self.version, []):
            patch(self, **it, strip=2)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.generate()

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()
        copy(self, "LICENSE*", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        rmdir(self, os.path.join(self.package_folder, "share"))
        rmdir(self, os.path.join(self.package_folder, "bin"))
        rm(self, "*Config*.cmake", os.path.join(self.package_folder, "lib", "cmake", "CGAL"))
        rm(self, "Find*.cmake", os.path.join(self.package_folder, "lib", "cmake", "CGAL"))

    @property
    def _module_file_rel_path(self):
        return os.path.join("lib", "cmake", f"conan-official-{self.name}-variables.cmake")

    @property
    def _module_subfolder(self):
        return os.path.join("lib", "cmake", "CGAL")

    def package_info(self):
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")
        self.cpp_info.builddirs.append(self._module_subfolder)
        self.cpp_info.set_property("cmake_find_package", "CGAL")
        self.cpp_info.set_property("cmake_target_name", "CGAL::CGAL")
