from conan import ConanFile
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir
import os

required_conan_version = ">=2.4"


class Gl2psConan(ConanFile):
    name = "gl2ps"
    description = "GL2PS: an OpenGL to PostScript printing library (also PDF, SVG, LaTeX and PGF output)"
    license = ("LGPL-2.0-or-later", "GL2PS")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://gitlab.onelab.info/gl2ps/gl2ps"
    topics = ("opengl", "postscript", "pdf", "svg", "vector-graphics", "printing")
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
    implements = ["auto_shared_fpic"]
    languages = "C"

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("opengl/system", transitive_headers=True, transitive_libs=True)
        self.requires("zlib/[>=1.2.11 <2]")
        self.requires("libpng/[>=1.6 <2]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        # INFO: GLUT is only used to build the upstream test programs, but it is also linked into the library
        tc.cache_variables["CMAKE_DISABLE_FIND_PACKAGE_GLUT"] = True
        tc.cache_variables["CMAKE_DISABLE_FIND_PACKAGE_LATEX"] = True
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "COPYING.*", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.libs = ["gl2ps"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")
        if self.settings.os == "Windows" and self.options.shared:
            # INFO: gl2ps.h uses dllimport only when GL2PSDLL is defined
            self.cpp_info.defines.append("GL2PSDLL")
