import functools
from conans import ConanFile, CMake, tools


class ImGuizmoConan(ConanFile):
    name = "imguizmo"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/CedricGuillemet/ImGuizmo"
    description = "Immediate mode 3D gizmo for scene editing and other controls based on Dear Imgui"
    topics = ("imgui", "3d", "graphics", "guizmo")
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
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def requirements(self):
        self.requires("imgui/1.87")

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.configure()
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["imguizmo"]
