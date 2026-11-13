from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir
import os

required_conan_version = ">=2.0.9"


class Gl2psConan(ConanFile):
    name = "gl2ps"
    description = "GL2PS: an OpenGL to PostScript printing library (also PDF, SVG, LaTeX and PGF output)"
    # SPDX has no identifier for the GL2PS license, which is offered as an alternative to the LGPL-2.0-or-later
    license = ("LGPL-2.0-or-later", "DocumentRef-COPYING.GL2PS:LicenseRef-GL2PS")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://gitlab.onelab.info/gl2ps/gl2ps"
    topics = ("opengl", "postscript", "pdf", "svg", "vector-graphics", "printing")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_zlib": [True, False],
        "with_png": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_zlib": True,
        "with_png": True,
    }
    implements = ["auto_shared_fpic"]

    def configure(self):
        # pure C project
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        # INFO: gl2ps.h includes <GL/gl.h> (<OpenGL/gl.h> on macOS)
        self.requires("opengl/system", transitive_headers=True, transitive_libs=True)
        if self.options.with_zlib:
            self.requires("zlib/[>=1.2.11 <2]")
        if self.options.with_png:
            self.requires("libpng/[>=1.6 <2]")

    def validate(self):
        # INFO: gl2ps.h only enables PNG support when ZLIB support is enabled too
        if self.options.with_png and not self.options.with_zlib:
            raise ConanInvalidConfiguration(f"{self.ref} requires with_zlib=True when with_png=True")

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.16]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["ENABLE_ZLIB"] = self.options.with_zlib
        tc.cache_variables["ENABLE_PNG"] = self.options.with_png
        # INFO: GLUT is only used to build the upstream test programs, but it is also linked into the library
        tc.cache_variables["CMAKE_DISABLE_FIND_PACKAGE_GLUT"] = True
        # INFO: upstream CMakeLists.txt tries to build the documentation when LaTeX is available
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
        # INFO: only README, licenses and test programs are installed in share/doc
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        # INFO: upstream does not provide any CMake config or pkg-config file.
        # The names below are the ones used by VTK's FindGL2PS module
        self.cpp_info.set_property("cmake_file_name", "GL2PS")
        self.cpp_info.set_property("cmake_target_name", "GL2PS::GL2PS")

        self.cpp_info.libs = ["gl2ps"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")
        if self.settings.os == "Windows" and self.options.shared:
            # INFO: gl2ps.h uses dllimport only when GL2PSDLL is defined
            self.cpp_info.defines.append("GL2PSDLL")
