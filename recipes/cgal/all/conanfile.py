import os
import textwrap
from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import get, replace_in_file, rmdir, rm, copy, save, export_conandata_patches, patch

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
        self._create_cmake_module_variables(
            os.path.join(self.package_folder, self._module_file_rel_path)
        )

    def _create_cmake_module_variables(self, module_file):
        content = textwrap.dedent(f"""\
            set(CGAL_MODULES_DIR {os.path.join(self.package_folder, "lib", "cmake", "CGAL")})
            list(APPEND CMAKE_MODULE_PATH ${{CGAL_MODULES_DIR}})
        """)
        save(self, module_file, content)

    @property
    def _module_file_rel_path(self):
        return os.path.join("lib", "cmake", f"conan-official-{self.name}-variables.cmake")

    def package_info(self):
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")
        self.cpp_info.set_property("cmake_find_package", "CGAL")
        self.cpp_info.set_property("cmake_target_name", "CGAL::CGAL")
        self.cpp_info.set_property("cmake_build_modules", [self._module_file_rel_path])
