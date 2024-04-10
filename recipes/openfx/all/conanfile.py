import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir

required_conan_version = ">=1.53.0"


class openfx(ConanFile):
    name = "openfx"
    description = "OpenFX image processing plug-in standard."
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://openeffects.org"
    topics = ("image-processing", "standard")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    def export_sources(self):
        copy(self, "CMakeLists.txt", src=self.recipe_folder, dst=self.export_sources_folder)
        copy(self, "*",
             src=os.path.join(self.recipe_folder, "cmake"),
             dst=os.path.join(self.export_sources_folder, "cmake"))
        copy(self, "*",
             src=os.path.join(self.recipe_folder, "symbols"),
             dst=os.path.join(self.export_sources_folder, "symbols"))

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        if self.settings.os in ["FreeBSD", "Linux"]:
            self.options["libglvnd"].glx = True

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if self.settings.os in ["FreeBSD", "Linux"]:
            self.requires("libglvnd/1.7.0")
        else:
            self.requires("opengl/system")
        self.requires("expat/2.5.0")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, 11)
        if self.settings.os in ["FreeBSD", "Linux"] and not self.dependencies["libglvnd"].options.glx:
            raise ConanInvalidConfiguration(f"{self.ref} requires the glx option of libglvnd to be enabled")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.generate()
        tc = CMakeDeps(self)
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure(build_script_folder=self.source_path.parent)
        cmake.build()

    @property
    def _build_modules(self):
        return [os.path.join("lib", "cmake", "OpenFX.cmake")]

    def package(self):
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        copy(self, "*.symbols",
             src=os.path.join(self.export_sources_folder, "symbols"),
             dst=os.path.join(self.package_folder, "lib", "symbols"))
        copy(self, "*.cmake",
             src=os.path.join(self.export_sources_folder, "cmake"),
             dst=os.path.join(self.package_folder, "lib", "cmake"))
        copy(self, "LICENSE",
             src=os.path.join(self.source_folder, "Support"),
             dst=os.path.join(self.package_folder, "licenses"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "openfx")
        self.cpp_info.set_property("cmake_target_name", "openfx::openfx")
        self.cpp_info.set_property("cmake_build_modules", self._build_modules)
        self.cpp_info.builddirs.append(os.path.join("lib", "cmake"))

        if self.options.shared:
            self.cpp_info.libs = ["OfxSupport"]
        else:
            self.cpp_info.libs = ["OfxHost", "OfxSupport"]

        if is_apple_os(self):
            self.cpp_info.frameworks = ["CoreFoundation", "OpenGL"]

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.names["cmake_find_package"] = "openfx"
        self.cpp_info.names["cmake_find_package_multi"] = "openfx"
        self.cpp_info.build_modules["cmake_find_package"] = self._build_modules
        self.cpp_info.build_modules["cmake_find_package_multi"] = self._build_modules
