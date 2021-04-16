from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os


class freeglutConan(ConanFile):
    name = "freeglut"
    description = "Open-source alternative to the OpenGL Utility Toolkit (GLUT) library"
    topics = ("conan", "freeglut", "opengl", "gl", "glut", "utility", "toolkit", "graphics")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/dcnieho/FreeGLUT"
    license = "X11"
    exports_sources = ["CMakeLists.txt", "*.patch"]
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "gles": [True, False],
        "print_errors_at_runtime": [True, False],
        "print_warnings_at_runtime": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "gles": False,
        "print_errors_at_runtime": True,
        "print_warnings_at_runtime": True,
    }

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
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        self.requires("opengl/system")
        self.requires('glu/system')
        if self.settings.os == "Linux":
            self.requires("xorg/system")

    def validate(self):
        if self.settings.os == "Macos":
            # see https://github.com/dcnieho/FreeGLUT/issues/27
            # and https://sourceforge.net/p/freeglut/bugs/218/
            # also, it seems to require `brew cask install xquartz`
            raise ConanInvalidConfiguration("%s does not support macos" % self.name)
        if (self.settings.compiler == "gcc" and self.settings.compiler.version >= tools.Version("10.0")) or \
            (self.settings.compiler == "clang" and self.settings.compiler.version >= tools.Version("11.0")):
            # see https://github.com/dcnieho/FreeGLUT/issues/86
            raise ConanInvalidConfiguration("%s does not support gcc >= 10 and clang >= 11" % self.name)

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = "FreeGLUT-FG_" + self.version.replace(".", "_")
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        # See https://github.com/dcnieho/FreeGLUT/blob/44cf4b5b85cf6037349c1c8740b2531d7278207d/README.cmake
        cmake = CMake(self, set_cmake_flags=True)

        cmake.definitions["FREEGLUT_BUILD_DEMOS"] = False
        cmake.definitions["FREEGLUT_BUILD_STATIC_LIBS"] = not self.options.shared
        cmake.definitions["FREEGLUT_BUILD_SHARED_LIBS"] = self.options.shared
        cmake.definitions["FREEGLUT_GLES"] = self.options.gles
        cmake.definitions["FREEGLUT_PRINT_ERRORS"] = self.options.print_errors_at_runtime
        cmake.definitions["FREEGLUT_PRINT_WARNINGS"] = self.options.print_warnings_at_runtime
        cmake.definitions["FREEGLUT_INSTALL_PDB"] = False
        cmake.definitions["INSTALL_PDB"] = False
        # cmake.definitions["FREEGLUT_WAYLAND"] = "ON" if self.options.wayland else "OFF" # nightly version only as of now

        cmake.configure(build_folder=self._build_subfolder)
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="COPYING", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)

        if self.settings.os == "Windows":
            if not self.options.shared:
                self.cpp_info.defines.append("FREEGLUT_STATIC=1")
            self.cpp_info.defines.append("FREEGLUT_LIB_PRAGMAS=0")
            self.cpp_info.system_libs.extends(["glu32", "gdi32", "winmm", "user32"])

        if self.settings.os == "Linux":
            self.cpp_info.system_libs.extends(["pthread", "m", "dl", "rt"])
