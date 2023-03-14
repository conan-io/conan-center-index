import os

from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, collect_libs, copy, export_conandata_patches, get, rmdir
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
        "spec": ["gl", "egl", "glx", "wgl"], # Name of the spec
        "extensions": ["ANY"], # Path to extensions file or comma separated list of extensions, if missing all extensions are included
        # if specification is gl
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
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

        if self.options.spec != "gl":
            del self.options.gl_profile
            del self.options.gl_version
            del self.options.gles1_version
            del self.options.gles2_version
            del self.options.glsc2_version

        if self.options.spec != "egl":
            del self.options.egl_version

        if self.options.spec != "glx":
            del self.options.glx_version

        if self.options.spec != "wgl":
            del self.options.wgl_version

    def validate(self):
        if self.options.spec == "wgl" and self.settings.os != "Windows":
            raise ConanInvalidConfiguration(f"{self.ref}:{self.options.spec} specification is not compatible with {self.settings.os}")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
    
    def generate(self):
        tc = CMakeToolchain(self)
        if "gl_profile" in self.options:
            tc.variables["GLAD_PROFILE"] = self.options.gl_profile
        tc.variables["GLAD_API"] = self._get_api()
        tc.variables["GLAD_EXTENSIONS"] = self.options.extensions
        tc.variables["GLAD_SPEC"] = self.options.spec
        tc.variables["GLAD_NO_LOADER"] = self.options.no_loader
        tc.variables["GLAD_GENERATOR"] = "c" if self.settings.build_type == "Release" else "c-debug"
        tc.variables["GLAD_EXPORT"] = True
        tc.variables["GLAD_INSTALL"] = True
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def _get_api(self):
        if self.options.spec == "gl":
            spec_api = {
                "gl": self.options.gl_version,
                "gles1": self.options.gles1_version,
                "gles2": self.options.gles2_version,
                "glsc2": self.options.glsc2_version
            }
        elif self.options.spec == "egl":
            spec_api = {"egl": self.options.egl_version}
        elif self.options.spec == "glx":
            spec_api = {"glx": self.options.glx_version}
        elif self.options.spec == "wgl":
            spec_api = {"wgl": self.options.wgl_version}

        api_concat = ",".join(f"{api_name}={api_version}".format()
                              for api_name, api_version in spec_api.items() if api_version != "None")

        return api_concat

    def package(self):
        CMake(self).install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))

    def package_info(self):
        self.cpp_info.libs = collect_libs(self)
        if self.options.shared:
            self.cpp_info.defines = ["GLAD_GLAPI_EXPORT"]
        if self.settings.os == "Linux":
            self.cpp_info.system_libs.append("dl")
