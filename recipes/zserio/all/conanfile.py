import os
import shutil

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import collect_libs, copy, download, get
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout

required_conan_version = ">=1.54.0"

class ZserioConanFile(ConanFile):
    name = "zserio"
    description = "Zserio C++ Runtime Library"
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index/"
    homepage = "https://zserio.org"
    topics = ("zserio", "cpp", "c++", "serialization")
    package_type = "static-library"
    settings = "os", "arch", "compiler", "build_type"

    options = { "fPIC": [True, False] }
    default_options = { "fPIC": False }

    @property
    def _min_cppstd(self):
        return 11

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def layout(self):
        cmake_layout(self, src_folder="src")

    def validate(self):
        if self.settings.os not in ["Linux", "Windows"]:
            raise ConanInvalidConfiguration("Zserio currently supports only Windows and Linux")

        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)

    def source(self):
        sources = self.conan_data["sources"][self.version]
        get(self, **sources["runtime"], strip_root=True)

    def export_sources(self):
        copy(self, "zserio_compiler.cmake", self.recipe_folder, self.export_sources_folder)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure(build_script_folder="cpp")
        cmake.build()

        sources = self.conan_data["sources"][self.version]

        get(self, **sources["compiler"], pattern="zserio.jar")

        download(self, filename="LICENSE", **sources["license"])

    @property
    def _cmake_module_path(self):
        return os.path.join("lib", "cmake", "zserio")

    def package(self):
        copy(self, "LICENSE", self.build_folder, os.path.join(self.package_folder, "licenses"))

        include_dir = os.path.join(self.package_folder, "include")
        lib_dir = os.path.join(self.package_folder, "lib")
        copy(self, "*.h", os.path.join(self.source_folder, "cpp"), include_dir)
        copy(self, "*.lib", self.build_folder, lib_dir, keep_path=False)
        copy(self, "*.a", self.build_folder, lib_dir, keep_path=False)

        copy(self, "zserio.jar", self.build_folder, os.path.join(self.package_folder, "bin"))
        copy(self, "zserio_compiler.cmake", self.export_sources_folder,
             os.path.join(self.package_folder, self._cmake_module_path))

    def package_info(self):
        self.cpp_info.components["ZserioCppRuntime"].libs = ["ZserioCppRuntime"]

        zserio_jar_file = os.path.join(self.package_folder, "bin", "zserio.jar")
        self.buildenv_info.define("ZSERIO_JAR_FILE", zserio_jar_file)

        self.cpp_info.builddirs.append(self._cmake_module_path)
        zserio_compiler_module = os.path.join(self.package_folder, self._cmake_module_path,
                                              "zserio_compiler.cmake")
        self.cpp_info.set_property("cmake_build_modules", [zserio_compiler_module])

        # TODO: remove in conan v2
        self.env_info.ZSERIO_JAR_FILE = zserio_jar_file
