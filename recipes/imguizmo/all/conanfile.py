import os
import glob
from conans import ConanFile, CMake, tools


class ImGuizmoConan(ConanFile):
    name = "imguizmo"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/CedricGuillemet/ImGuizmo"
    description = "Immediate mode 3D gizmo for scene editing and other controls based on Dear Imgui"
    topics = ("conan", "imgui", "3d", "graphics", "guizmo")
    license = "MIT"
    settings = "os", "arch", "compiler", "build_type"

    exports_sources = ["CMakeLists.txt"]
    generators = "cmake"

    options = {
        "shared": [True, False],
         "fPIC": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True
    }

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = glob.glob("ImGuizmo-*/")[0]
        os.rename(extracted_dir, self._source_subfolder)

    def requirements(self):
        if self.version == "cci.20210223":
            self.requires("imgui/1.82")
        else:
            self.requires("imgui/1.83")

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.configure()
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["imguizmo"]
