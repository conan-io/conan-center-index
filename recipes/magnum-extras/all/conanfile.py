from conans import ConanFile, CMake, tools
from conan.errors import ConanInvalidConfiguration
import functools
import os

required_conan_version = ">=1.43.0"


class MagnumExtrasConan(ConanFile):
    name = "magnum-extras"
    description = "Extras for the Magnum C++11/C++14 graphics engine"
    license = "MIT"
    topics = ("magnum", "graphics", "rendering", "3d", "2d", "opengl")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://magnum.graphics"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "player": [True, False],
        "ui": [True, False],
        "ui_gallery": [True, False],
        "application": ["android", "emscripten", "glfw", "glx", "sdl2", "xegl"],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "player": True,
        "ui": True,
        "ui_gallery": True,
        "application": "sdl2",
    }

    short_paths = True
    generators = "cmake", "cmake_find_package"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def export_sources(self):
        self.copy("CMakeLists.txt")
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

        if self.settings.os == "Android":
            self.options.application = "android"
        if self.settings.os == "Emscripten":
            self.options.application = "emscripten"
            # FIXME: Requires 'magnum:basis_importer=True'
            self.options.player = False
            # FIXME: Fails to compile
            self.options.ui_gallery = False

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        self.requires("magnum/{}".format(self.version))
        self.requires("corrade/{}".format(self.version))
        if self.settings.os in ["iOS", "Emscripten", "Android"] and self.options.ui_gallery:
            self.requires("magnum-plugins/{}".format(self.version))

    def validate(self):
        opt_name = "{}_application".format(self.options.application)
        if not getattr(self.options["magnum"], opt_name):
            raise ConanInvalidConfiguration("Magnum needs option '{opt}=True'".format(opt=opt_name))
        if self.settings.os == "Emscripten" and self.options["magnum"].target_gl == "gles2":
            raise ConanInvalidConfiguration("OpenGL ES 3 required, use option 'magnum:target_gl=gles3'")

    def build_requirements(self):
        self.build_requires("corrade/{}".format(self.version))

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["BUILD_STATIC"] = not self.options.shared
        cmake.definitions["BUILD_STATIC_PIC"] = self.options.get_safe("fPIC", False)
        cmake.definitions["BUILD_TESTS"] = False
        cmake.definitions["BUILD_GL_TESTS"] = False

        cmake.definitions["WITH_PLAYER"] = self.options.player
        cmake.definitions["WITH_UI"] = self.options.ui
        cmake.definitions["WITH_UI_GALLERY"] = self.options.ui_gallery

        cmake.configure()
        return cmake

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)

        tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"),
                              'set(CMAKE_MODULE_PATH "${PROJECT_SOURCE_DIR}/modules/" ${CMAKE_MODULE_PATH})',
                              "")

        cmakelists = [os.path.join("src", "Magnum", "Ui", "CMakeLists.txt"),
                      os.path.join("src", "player","CMakeLists.txt")]
        app_name = "{}Application".format("XEgl" if self.options.application == "xegl" else str(self.options.application).capitalize())
        for cmakelist in cmakelists:
            tools.replace_in_file(os.path.join(self._source_subfolder, cmakelist),
                                  "Magnum::Application",
                                  "Magnum::{}".format(app_name))

    def build(self):
        self._patch_sources()

        cm = self._configure_cmake()
        cm.build()

    def package(self):
        cm = self._configure_cmake()
        cm.install()

        tools.rmdir(os.path.join(self.package_folder, "share"))
        self.copy("COPYING", src=self._source_subfolder, dst="licenses")

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "MagnumExtras")
        self.cpp_info.names["cmake_find_package"] = "MagnumExtras"
        self.cpp_info.names["cmake_find_package_multi"] = "MagnumExtras"

        lib_suffix = "-d" if self.settings.build_type == "Debug" else ""
        if self.options.ui:
            self.cpp_info.components["ui"].set_property("cmake_target_name", "MagnumExtras::Ui")
            self.cpp_info.components["ui"].names["cmake_find_package"] = "Ui"
            self.cpp_info.components["ui"].names["cmake_find_package_multi"] = "Ui"
            self.cpp_info.components["ui"].libs = ["MagnumUi{}".format(lib_suffix)]
            self.cpp_info.components["ui"].requires = ["corrade::interconnect", "magnum::magnum_main", "magnum::gl", "magnum::text"]

        if self.options.player or self.options.ui_gallery:
            bin_path = os.path.join(self.package_folder, "bin")
            self.output.info('Appending PATH environment variable: %s' % bin_path)
            self.env_info.path.append(bin_path)
