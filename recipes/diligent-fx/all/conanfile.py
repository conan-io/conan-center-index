import os
from conan import ConanFile
from conans import CMake
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import get, collect_libs, export_conandata_patches, apply_conandata_patches, rename
import shutil

required_conan_version = ">=1.52.0"

class DiligentFxConan(ConanFile):
    name = "diligent-fx"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/DiligentGraphics/DiligentFx/"
    description = "DiligentFX is the Diligent Engine's high-level rendering framework."
    license = ("Apache-2.0")
    topics = ("graphics", "game-engine", "renderer", "graphics-library")
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], 
    "fPIC":         [True, False],
    }
    default_options = {"shared": False, 
    "fPIC": True,
    }
    generators = "cmake_find_package", "cmake"
    _cmake = None
    short_paths = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def export_sources(self):
        export_conandata_patches(self)
        self.copy("CMakeLists.txt")
        self.copy("BuildUtils.cmake")
        self.copy("script.py")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)

    def validate(self):
        if self.options.shared:
            raise ConanInvalidConfiguration("Can't build as a shared lib")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def _patch_sources(self):
        apply_conandata_patches(self)

    def requirements(self):
        if self.version == "cci.20220219" or self.version == "cci.20211112":
            self.requires("diligent-tools/2.5.2")
        else:
            self.requires("diligent-tools/{}".format(self.version))

    @property
    def _diligent_platform(self):
        if self.settings.os == "Windows":
            return "PLATFORM_WIN32"
        elif self.settings.os == "Macos":
            return "PLATFORM_MACOS"
        elif self.settings.os == "Linux":
            return "PLATFORM_LINUX"
        elif self.settings.os == "Android":
            return "PLATFORM_ANDROID"
        elif self.settings.os == "iOS":
            return "PLATFORM_IOS"
        elif self.settings.os == "Emscripten":
            return "PLATFORM_EMSCRIPTEN"
        elif self.settings.os == "watchOS":
            return "PLATFORM_TVOS"

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["DILIGENT_NO_FORMAT_VALIDATION"] = True
        self._cmake.definitions["DILIGENT_BUILD_TESTS"] = False

        self._cmake.definitions[self._diligent_platform] = True
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        self.copy("License.txt", dst="licenses", src=self._source_subfolder)
        rename(self, src=os.path.join(self.package_folder, "include", "source_subfolder"),
                     dst=os.path.join(self.package_folder, "include", "DiligentFx"))
        shutil.move(os.path.join(self.package_folder, "Shaders"), 
                    os.path.join(self.package_folder, "res", "Shaders"))

        self.copy(pattern="*.dll", src=self._build_subfolder, dst="bin", keep_path=False)
        self.copy(pattern="*.dylib", src=self._build_subfolder, dst="lib", keep_path=False)
        self.copy(pattern="*.lib", src=self._build_subfolder, dst="lib", keep_path=False)
        self.copy(pattern="*.a", src=self._build_subfolder, dst="lib", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = collect_libs(self)
        self.cpp_info.includedirs.append(os.path.join("include", "DiligentFx"))
        self.cpp_info.includedirs.append(os.path.join("include", "DiligentFx", "Components", "interface"))
        self.cpp_info.includedirs.append(os.path.join("include", "DiligentFx", "GLTF_PBR_Renderer", "interface"))
        self.cpp_info.includedirs.append(os.path.join("include", "DiligentFx", "PostProcess", "EpipolarLightScattering", "interface"))
        self.cpp_info.includedirs.append(os.path.join("res"))


