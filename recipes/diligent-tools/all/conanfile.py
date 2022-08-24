import os
from conan import ConanFile, tools
from conans import CMake
from conan.errors import ConanInvalidConfiguration

required_conan_version = ">=1.33.0"

class DiligentToolsConan(ConanFile):
    name = "diligent-tools"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/DiligentGraphics/DiligentTools/"
    description = "Diligent Core is a modern cross-platfrom low-level graphics API."
    license = ("Apache-2.0")
    topics = ("graphics", "texture", "gltf", "draco", "imgui")
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], 
               "fPIC": [True, False]}
    default_options = {"shared": False, 
                       "fPIC": True}
    generators = "cmake_find_package", "cmake"
    _cmake = None
    exports_sources = ["CMakeLists.txt", "patches/**", "BuildUtils.cmake"]
    short_paths = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)

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
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.patch(self, **patch)

    def validate(self):
        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, 11)
        if self.options.shared:
            raise ConanInvalidConfiguration("Can't build diligent tools as shared lib")

    def requirements(self):
        if self.version == "cci.20211009":
            self.requires("diligent-core/2.5.1")
            self.requires("imgui/1.87")
        else:
            self.requires("diligent-core/{}".format(self.version))
            self.requires('taywee-args/6.3.0')
            self.requires("imgui/1.85")

        self.requires("libjpeg/9d")
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
        tools.files.rmdir(self, os.path.join(self.package_folder, "Licenses"))
        self.copy("License.txt", dst="licenses", src=self._source_subfolder)

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.includedirs.append(os.path.join("include", "DiligentTools"))
        self.cpp_info.includedirs.append(os.path.join("include", "DiligentTools", "AssetLoader", "interface"))

        self.cpp_info.defines.append(f"{self._diligent_platform}=1")

        if self.settings.os in ["Macos", "Linux"]:
            self.cpp_info.system_libs = ["dl", "pthread"]
        if self.settings.os == 'Macos':
            self.cpp_info.frameworks = ["CoreFoundation", 'Cocoa']
