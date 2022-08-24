import os

from conans import ConanFile, CMake, tools
from conan.errors import ConanInvalidConfiguration

class GladConan(ConanFile):
    name = "glad"
    description = "Multi-Language GL/GLES/EGL/GLX/WGL Loader-Generator based on the official specs."
    topics = ("conan", "glad", "opengl")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/Dav1dde/glad"
    license = "MIT"
    exports_sources = ["CMakeLists.txt", "patches/*.patch"]
    generators = "cmake"
    settings = "os", "compiler", "build_type", "arch"

    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "no_loader": [True, False],
        "spec": ["gl", "egl", "glx", "wgl"], # Name of the spec
        "extensions": "ANY", # Path to extensions file or comma separated list of extensions, if missing all extensions are included
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
        "extensions": "''",
        "gl_profile": "compatibility",
        "gl_version": "3.3",
        "gles1_version": "None",
        "gles2_version": "None",
        "glsc2_version": "None",
        "egl_version": "None",
        "glx_version": "None",
        "wgl_version": "None"
    }

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

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

        if self.options.spec == "wgl" and self.settings.os != "Windows":
            raise ConanInvalidConfiguration("{0} specification is not compatible with {1}".format(self.options.spec,
                                                                                                  self.settings.os))

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        if "gl_profile" in self.options:
            self._cmake.definitions["GLAD_PROFILE"] = self.options.gl_profile
        self._cmake.definitions["GLAD_API"] = self._get_api()
        self._cmake.definitions["GLAD_EXTENSIONS"] = self.options.extensions
        self._cmake.definitions["GLAD_SPEC"] = self.options.spec
        self._cmake.definitions["GLAD_NO_LOADER"] = self.options.no_loader
        self._cmake.definitions["GLAD_GENERATOR"] = "c" if self.settings.build_type == "Release" else "c-debug"
        self._cmake.definitions["GLAD_EXPORT"] = True
        self._cmake.definitions["GLAD_INSTALL"] = True

        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

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

        api_concat = ",".join("{0}={1}".format(api_name, api_version)
                              for api_name, api_version in spec_api.items() if api_version != "None")

        return api_concat

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))

        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if self.options.shared:
            self.cpp_info.defines = ["GLAD_GLAPI_EXPORT"]
        if self.settings.os == "Linux":
            self.cpp_info.system_libs.append("dl")
