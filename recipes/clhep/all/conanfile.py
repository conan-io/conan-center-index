from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, get
from conan.tools.microsoft import is_msvc
import os

required_conan_version = ">=1.50.0"


class ClhepConan(ConanFile):
    name = "clhep"
    description = "Class Library for High Energy Physics."
    license = "LGPL-3.0-only"
    topics = ("clhep", "cern", "hep", "high energy", "physics", "geometry", "algebra")
    homepage = "http://proj-clhep.web.cern.ch/proj-clhep"
    url = "https://github.com/conan-io/conan-center-index"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    short_paths = True

    def export_sources(self):
        for p in self.conan_data.get("patches", {}).get(self.version, []):
            copy(self, p["patch_file"], self.recipe_folder, self.export_sources_folder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def validate(self):
        if self.info.settings.compiler.cppstd:
            check_min_cppstd(self, 11)
        if is_msvc(self) and self.info.options.shared:
            raise ConanInvalidConfiguration("CLHEP doesn't properly build its shared libs with Visual Studio")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["CLHEP_SINGLE_THREAD"] = False
        tc.variables["CLHEP_BUILD_DOCS"] = False
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure(build_script_folder=os.path.join(self.source_folder, "CLHEP"))
        cmake.build()

    def package(self):
        copy(self, "COPYING*", src=os.path.join(self.source_folder, "CLHEP"), dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

    @property
    def _clhep_components(self):
        def libm():
            return ["m"] if self.settings.os in ["Linux", "FreeBSD"] else []

        def pthread():
            return ["pthread"] if self.settings.os in ["Linux", "FreeBSD"] else []

        return [
            {"name": "Vector", "system_libs": libm() + pthread()},
            {"name": "Evaluator", "system_libs": libm() + pthread()},
            {"name": "GenericFunctions", "system_libs": libm() + pthread()},
            {"name": "Geometry", "system_libs": libm() + pthread(), "requires": ["vector"]},
            {"name": "Random", "system_libs": libm() + pthread()},
            {"name": "Matrix", "system_libs": libm() + pthread(), "requires": ["random", "vector"]},
            {"name": "RandomObjects", "system_libs": libm(), "requires": ["random", "matrix", "vector"]},
            {"name": "Cast", "system_libs": pthread()},
            {"name": "RefCount", "system_libs": pthread()},
            {"name": "Exceptions", "requires": ["cast", "refcount"]},
        ]

    def package_info(self):
        suffix = "" if self.options.shared else "S"

        self.cpp_info.set_property("cmake_file_name", "CLHEP")
        self.cpp_info.set_property("cmake_target_name", f"CLHEP::CLHEP{suffix}")
        self.cpp_info.set_property("pkg_config_name", "clhep")

        for component in self._clhep_components:
            name = component["name"]
            conan_comp = name.lower()
            cmake_target = f"{name}{suffix}"
            pkg_config_name = f"clhep-{name.lower()}"
            lib_name = f"CLHEP-{name}-{self.version}"
            system_libs = component.get("system_libs", [])
            requires = component.get("requires", [])

            self.cpp_info.components[conan_comp].set_property("cmake_target_name", f"CLHEP::{cmake_target}")
            self.cpp_info.components[conan_comp].set_property("pkg_config_name", pkg_config_name)
            self.cpp_info.components[conan_comp].libs = [lib_name]
            self.cpp_info.components[conan_comp].system_libs = system_libs
            self.cpp_info.components[conan_comp].requires = requires

            # TODO: to remove in conan v2 once cmake_find_package* generators removed
            self.cpp_info.components[conan_comp].names["cmake_find_package"] = cmake_target
            self.cpp_info.components[conan_comp].names["cmake_find_package_multi"] = cmake_target
            self.cpp_info.components[conan_comp].names["pkg_config"] = pkg_config_name
            self.cpp_info.components["clheplib"].requires.append(conan_comp)

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.names["cmake_find_package"] = "CLHEP"
        self.cpp_info.names["cmake_find_package_multi"] = "CLHEP"
        self.cpp_info.names["pkg_config"] = "clhep"
        self.cpp_info.components["clheplib"].names["cmake_find_package"] = f"CLHEP{suffix}"
        self.cpp_info.components["clheplib"].names["cmake_find_package_multi"] = f"CLHEP{suffix}"
        self.cpp_info.components["clheplib"].set_property("cmake_target_name", f"CLHEP::CLHEP{suffix}")
        self.cpp_info.components["clheplib"].names["pkg_config"] = "clhep"
        self.cpp_info.components["clheplib"].set_property("pkg_config_name", "clhep")
