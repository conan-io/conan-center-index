import os
import sys
from pathlib import Path

from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get
from conan.errors import ConanInvalidConfiguration

class GladConan(ConanFile):
    name = "glad"
    description = "Multi-Language GL/GLES/EGL/GLX/WGL Loader-Generator based on the official specs."
    topics = ("opengl",)
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/Dav1dde/glad"
    license = "MIT"
    settings = "os", "compiler", "build_type", "arch"
    package_type = "library"

    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "no_loader": [True, False],
        "extensions": ["ANY"],
        "debug_layer": [True, False],
        "multicontext": [True, False],
        "gl_profile": ["compatibility", "core"],
        "gl_version": ["None", "1.0", "1.1", "1.2", "1.3", "1.4", "1.5", "2.0",
                       "2.1", "3.0", "3.1", "3.2", "3.3", "4.0", "4.1", "4.2",
                       "4.3", "4.4", "4.5", "4.6"],
        "gles1_version": ["None", "1.0"],
        "gles2_version": ["None", "2.0", "3.0", "3.1", "3.2"],
        "glsc2_version": ["None", "2.0"],
        "egl_version": ["None", "1.0", "1.1", "1.2", "1.3", "1.4", "1.5"],
        "glx_version": ["None", "1.0", "1.1", "1.2", "1.3", "1.4"],
        "wgl_version": ["None", "1.0"]
    }

    options_description = {
        "extensions": "A comma separated list of extensions, if missing all extensions are included",
        "debug_layer": "Enable the additional GLAD debug wrappers"
    }

    default_options = {
        "shared": False,
        "fPIC": True,
        "no_loader": False,
        "extensions": "",
        "debug_layer": False,
        "multicontext": False,
        "gl_profile": "compatibility",
        "gl_version": "3.3",
        "gles1_version": "None",
        "gles2_version": "None",
        "glsc2_version": "None",
        "egl_version": "None",
        "glx_version": "None",
        "wgl_version": "None"
    }

    def export_sources(self):
        copy(self, "CMakeLists.txt", self.recipe_folder, self.export_sources_folder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        else:
            del self.options.wgl_version
        self.options.debug_layer = self.settings.build_type == "Debug"

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def validate(self):
        if (self.options.gles1_version != "None" or self.options.gles2_version != "None") and self.options.egl_version == "None":
            raise ConanInvalidConfiguration(f"{self.ref} Generating an OpenGLES spec requires a valid version of EGL")
        if self.options.debug_layer and self.options.multicontext:
            raise ConanInvalidConfiguration("The multicontext and debug layer options are incompatible")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        if os.getenv("CONAN_CENTER_BUILD_SERVICE"):
            # We need the Jinja2 package for Glad's code generation,
            # but the Python found by CMake's FindPython may not have it installed.
            # For CCI runners, we know that the Python running Conan will definitely have it.
            tc.cache_variables["Python_EXECUTABLE"] = sys.executable

        tc.cache_variables.update({
                "GLAD_SOURCES_DIR": self.source_folder,
                "GLAD_CONAN_LIB_TYPE": "SHARED" if self.options.shared else "STATIC",
                "GLAD_CONAN_API": self._get_api(),
        })
        if self.options.extensions:
            tc.cache_variables["GLAD_CONAN_EXTENSIONS"] = ";".join(str(self.options.extensions).split(","))

        if not self.options.no_loader:
            tc.cache_variables["GLAD_CONAN_LOADER"] = "LOADER"

        if self.options.debug_layer:
            # wraps all gl calls in a debugging layer - can be used independently of the
            # conan build type
            # See https://github.com/Dav1dde/glad/wiki/C#debugging
            tc.cache_variables["GLAD_CONAN_DEBUG"] = "DEBUG"

        if self.options.multicontext:
            tc.cache_variables["GLAD_CONAN_MX"] = "MX"

        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure(build_script_folder=Path(self.source_folder).parent)
        cmake.build()

    def _get_api(self):
        spec_api = {
            "gl": self.options.gl_version,
            "gles1": self.options.gles1_version,
            "gles2": self.options.gles2_version,
            "glsc2": self.options.glsc2_version,
            "egl": self.options.egl_version,
            "glx": self.options.glx_version,
            "wgl": self.options.get_safe("wgl_version", "None")
        }
        return ";".join(
            f"{name}:{self.options.gl_profile}={version}" if name == "gl" else f"{name}={version}"
            for name, version in spec_api.items()
            if version != "None"
        )

    def package(self):
        CMake(self).install()
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))

    def package_info(self):
        self.cpp_info.libs = ["glad"]
        if self.options.shared:
            self.cpp_info.defines = ["GLAD_API_CALL_EXPORT"]
        if self.settings.os == "Linux":
            self.cpp_info.system_libs.append("dl")
