import os
from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import get, replace_in_file, rmdir, copy, export_conandata_patches, patch
from conan.tools import scm

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

    def _patch_sources(self):
        if scm.Version(self.version) < "5.3":
            replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"),
                            "CMAKE_SOURCE_DIR", "CMAKE_CURRENT_SOURCE_DIR", strict=False)
        else:
            replace_in_file(self,  os.path.join(self.source_folder, "CMakeLists.txt"),
                            "if(NOT PROJECT_NAME)", "if(1)", strict=False)
        for it in self.conan_data.get("patches", {}).get(self.version, []):
            patch(self, **it, strip=2)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        if scm.Version(self.version) < "5.3":
            tc.variables["CGAL_HEADER_ONLY"] = True
        tc.generate()

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE*", dst="licenses", src="src")
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "share"))
        rmdir(self, os.path.join(self.package_folder, "bin"))

    def package_info(self):
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")
        self.cpp_info.set_property("cmake_find_package", "CGAL")
        self.cpp_info.set_property("cmake_target_name", "CGAL::CGAL")
        self.cpp_info.set_property("cmake_build_modules", [os.path.join("lib", "cmake", "CGAL", "CGALConfig.cmake")])
        if scm.Version(self.version) < "5.3":
            self.cpp_info.defines.append("CGAL_HEADER_ONLY=1")
