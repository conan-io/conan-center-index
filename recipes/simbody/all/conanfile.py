from conan import ConanFile, tools
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake, CMakeToolchain
from conan.tools.scm import Version
from conan.tools.files import copy, get, rmdir, save
import os
import textwrap

required_conan_version = ">=1.50.0"

class SimbodyConan(ConanFile):
    name = "simbody"
    description = "High-performance, open-source toolkit for science- and engineering-quality simulation"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/simbody/simbody"
    topics = ("high-performance", "science", "simulation")
    settings = "os", "compiler", "build_type", "arch"
    exports_sources = "CMakeLists.txt"
    options = {
        "shared": [True, False],
        "fPIC": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True
    }

    def validate(self):
        if not self.dependencies["openblas"].options.build_lapack:
            raise ConanInvalidConfiguration(f"{self.name} requires the openblas:build_lapack": True")


    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    @property
    def _module_file_rel_path(self):
        return os.path.join("lib", "cmake", f"conan-official-{self.name}-variables.cmake")

    def requirements(self):
        self.requires("openblas/0.3.17")
        self.requires("opengl/system")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],  
                    destination=self.source_folder, strip_root=True)

    def layout(self):
        cmake_layout(self, src_folder="Simbody/src")

    def generate(self):
        tc.generate()
        tc = CMakeDeps(self)
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        

    @staticmethod
    def _create_cmake_module_variables(self, module_file, version):
        content = textwrap.dedent("""\
            set(simbody_VERSION_MAJOR {major})
            set(simbody_VERSION_MINOR {minor})
            set(simbody_VERSION_PATCH {patch})
            set(simbody_VERSION_STRING "{major}.{minor}.{patch}")
        """.format(major=version.major, minor=version.minor, patch=version.patch))
        save(self, module_file, content)

    def package_info(self):
        version_major = Version(self.version).major
        simbody_cmake_component = f"simbody{version_major}"
        base_module_path = os.path.join(self.package_folder, "lib", "cmake", simbody_cmake_component)
        
        self.cpp_info.names["cmake_find_package"] = simbody_cmake_component
        self.cpp_info.names["cmake_find_package_multi"] = simbody_cmake_component

        self.cpp_info.components[simbody_cmake_component].names["cmake_find_package"] = simbody_cmake_component
        self.cpp_info.components[simbody_cmake_component].names["cmake_find_package_multi"] = simbody_cmake_component
        self.cpp_info.components[simbody_cmake_component].builddirs.append(os.path.join(base_module_path, f"cmake{version_major}"))
