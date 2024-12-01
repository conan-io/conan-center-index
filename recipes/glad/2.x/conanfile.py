import os
import sys
from pathlib import Path

from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import collect_libs, copy, get
from conan.errors import ConanInvalidConfiguration

class GladConan(ConanFile):
    name = "glad"
    description = "Multi-Language GL/GLES/EGL/GLX/WGL Loader-Generator based on the official specs."
    topics = ("opengl",)
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/Dav1dde/glad"
    license = "MIT"
    settings = "os", "compiler", "build_type", "arch"

    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "no_loader": [True, False],
        "spec": ["gl", "egl", "glx", "wgl"], # Not relevant for 2.x. A spec will be included unless its version is None
        "extensions": ["ANY"], # A comma separated list of extensions, if missing all extensions are included
        "debug": [True, False], # Enable the Debugging layer (only available if build_type=Debug)

        "gl_profile": ["compatibility", "core"],
        "gl_version": ["None", "1.0", "1.1", "1.2", "1.3", "1.4", "1.5", "2.0",
                       "2.1", "3.0", "3.1", "3.2", "3.3", "4.0", "4.1", "4.2",
                       "4.3", "4.4", "4.5", "4.6"],
        "gles1_version": ["None", "1.0"],
        "gles2_version": ["None", "2.0", "3.0", "3.1", "3.2"],
        "glsc2_version": ["None", "2.0"],
        # if specification is egl
        "egl_version": ["None", "1.0", "1.1", "1.2", "1.3", "1.4", "1.5"],
        # if specification is glx
        "glx_version": ["None", "1.0", "1.1", "1.2", "1.3", "1.4"],
        # if specification is wgl
        "wgl_version": ["None", "1.0"]
    }

    default_options = {
        "shared": False,
        "fPIC": True,
        "no_loader": False,
        "spec": "gl",
        "extensions": "",
        "debug": True,
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
            del self.options.wgl_version
        if self.settings.build_type != "Debug":
            del self.options.debug

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def validate(self):
        if (self.options.gles1_version != "None" or self.options.gles2_version != "None") and self.options.egl_version == "None":
            raise ConanInvalidConfiguration(f"{self.ref} Generating an OpenGLES spec requires a valid version of EGL")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
    
    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables.update({
                "Python_EXECUTABLE": sys.executable,
                "GLAD_SOURCES_DIR": self.source_folder,
                "GLAD_CONAN_LIB_TYPE": "SHARED" if self.options.shared else "STATIC",
                "GLAD_CONAN_API": self._get_api(),
                "GLAD_CONAN_EXTENSIONS": ";".join(str(self.options.extensions).split(","))
        })

        if not self.options.no_loader:
            tc.cache_variables["GLAD_CONAN_LOADER"] = "LOADER"

        if self.settings.build_type == "Debug" and self.options.get_safe("debug"):
            # This is more than just debug symbols - it wraps all gl calls in a debugging layer.
            # See https://github.com/Dav1dde/glad/wiki/C#debugging
            tc.cache_variables["GLAD_CONAN_DEBUG"] = "DEBUG"

        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure(build_script_folder=Path(self.source_folder).parent)
        cmake.build()

    def _get_api(self):
        def api(spec):
            for api_name, api_version in spec.items():
                if api_version == "None":
                    continue
                if api_name == "gl":
                    yield f"{api_name}:{self.options.gl_profile}={api_version}"
                else:
                    yield f"{api_name}={api_version}"

        spec_api = {
            "gl": self.options.gl_version,
            "gles1": self.options.gles1_version,
            "gles2": self.options.gles2_version,
            "glsc2": self.options.glsc2_version,
            "egl": self.options.egl_version,
            "glx": self.options.glx_version,
        }

        wgl_version = self.options.get_safe("wgl_version")
        if wgl_version:
            spec_api["wgl"] = wgl_version

        return ";".join(api(spec_api))

    def package(self):
        CMake(self).install()
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))

    def package_info(self):
        self.cpp_info.libs = collect_libs(self)
        if self.options.shared:
            self.cpp_info.defines = ["GLAD_API_CALL_EXPORT"]
        if self.settings.os == "Linux":
            self.cpp_info.system_libs.append("dl")
