import os
from conan import ConanFile
from conans import CMake
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.files import get, rmdir, rm, collect_libs, patches, export_conandata_patches
from conan.tools.scm import Version

required_conan_version = ">=1.52.0"

class DiligentToolsConan(ConanFile):
    name = "diligent-tools"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/DiligentGraphics/DiligentTools/"
    description = "Diligent Core is a modern cross-platfrom low-level graphics API."
    license = ("Apache-2.0")
    topics = ("graphics", "texture", "gltf", "draco", "imgui")
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], 
               "fPIC": [True, False],
               "jpeg": [False, "libjpeg-turbo", "libjpeg"],
               "with_render_state_packager": [True, False],
               "with_archiver": [True, False],
              }
    default_options = {"shared": False, 
                       "fPIC": True,
                       "jpeg": "libjpeg",
                       "with_render_state_packager": False,
                       "with_archiver": True,
                      }

    generators = "cmake_find_package", "cmake_find_package_multi", "cmake"
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

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)

    def package_id(self):
        if self.settings.compiler == "Visual Studio":
            if "MD" in self.settings.compiler.runtime:
                self.info.settings.compiler.runtime = "MD/MDd"
            else:
                self.info.settings.compiler.runtime = "MT/MTd"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def _patch_sources(self):
        patches.apply_conandata_patches(self)

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, 11)
        if self.options.shared:
            raise ConanInvalidConfiguration("Can't build diligent tools as shared lib")

    def build_requirements(self):
        self.tool_requires("cmake/3.24.2")

    def requirements(self):
        if self.version == "cci.20211009":
            self.requires("diligent-core/2.5.1")
            self.requires("imgui/1.87")
        else:
            self.requires("diligent-core/{}".format(self.version))
            self.requires('taywee-args/6.3.0')
            self.requires("imgui/1.85")

        if self.options.jpeg == "libjpeg":
            self.requires("libjpeg/9e")
        if self.options.jpeg == "libjpeg-turbo":
            self.requires("libjpeg-turbo/2.1.4")
        self.requires("libpng/1.6.37")
        self.requires("libtiff/4.3.0")
        self.requires("zlib/1.2.12")

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

        self._cmake.definitions["DILIGENT_INSTALL_TOOLS"] = False
        self._cmake.definitions["DILIGENT_BUILD_SAMPLES"] = False
        self._cmake.definitions["DILIGENT_NO_FORMAT_VALIDATION"] = True
        self._cmake.definitions["DILIGENT_BUILD_TESTS"] = False
        self._cmake.definitions["DILIGENT_BUILD_TOOLS_TESTS"] = False
        self._cmake.definitions["DILIGENT_BUILD_TOOLS_INCLUDE_TEST"] = False
        self._cmake.definitions["DILIGENT_NO_RENDER_STATE_PACKAGER"] = not self.options.with_render_state_packager
        self._cmake.definitions["ARCHIVER_SUPPORTED"] = not self.options.with_archiver

        if self.version != "cci.20211009" and \
        (self.version.startswith("api") and self.version >= "api.252005") or \
        (self.version > "2.5.2"):
            self._cmake.definitions["GL_SUPPORTED"] = True
            self._cmake.definitions["GLES_SUPPORTED"] = True
            self._cmake.definitions["VULKAN_SUPPORTED"] = True
            self._cmake.definitions["METAL_SUPPORTED"] = True

        self._cmake.definitions[self._diligent_platform] = True
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("*.hpp", src=self._source_subfolder, dst="include/DiligentTools", keep_path=True)        
        self.copy(pattern="*.dll", src=self._build_subfolder, dst="bin", keep_path=False)
        self.copy(pattern="*.dylib", src=self._build_subfolder, dst="lib", keep_path=False)
        self.copy(pattern="*.lib", src=self._build_subfolder, dst="lib", keep_path=False)
        self.copy(pattern="*.a", src=self._build_subfolder, dst="lib", keep_path=False)
        self.copy("*", src=os.path.join(self._build_subfolder, "bin"), dst="bin", keep_path=False)
        rmdir(self, os.path.join(self.package_folder, "Licenses"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "bin"))
        self.copy("License.txt", dst="licenses", src=self._source_subfolder)

    def package_info(self):
        self.cpp_info.libs = collect_libs(self)
        self.cpp_info.includedirs.append(os.path.join("include", "DiligentTools"))
        self.cpp_info.includedirs.append(os.path.join("include", "DiligentTools", "AssetLoader", "interface"))

        self.cpp_info.defines.append(f"{self._diligent_platform}=1")

        if self.settings.os in ["Macos", "Linux"]:
            self.cpp_info.system_libs = ["dl", "pthread"]
        if self.settings.os == 'Macos':
            self.cpp_info.frameworks = ["CoreFoundation", 'Cocoa']
