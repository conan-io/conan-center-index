import os
from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout, CMakeDeps
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.files import get, rmdir, rm, collect_libs, patches, export_conandata_patches, copy, apply_conandata_patches
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

    generators = "cmake_find_package", "cmake_find_package_multi"
    _cmake = None
    short_paths = True

    def export_sources(self):
        copy(self, "CMakeLists.txt", src=self.recipe_folder, dst=self.export_sources_folder, keep_path=False)
        copy(self, "BuildUtils.cmake", src=self.recipe_folder, dst=self.export_sources_folder, keep_path=False)
        export_conandata_patches(self)

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=os.path.join(self.source_folder, "source_subfolder"), strip_root=True)

    def package_id(self):
        if self.settings.compiler == "Visual Studio":
            if "MD" in self.settings.compiler.runtime:
                self.info.settings.compiler.runtime = "MD/MDd"
            else:
                self.info.settings.compiler.runtime = "MT/MTd"

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["DILIGENT_INSTALL_TOOLS"] = False
        tc.variables["DILIGENT_BUILD_SAMPLES"] = False
        tc.variables["DILIGENT_NO_FORMAT_VALIDATION"] = True
        tc.variables["DILIGENT_BUILD_TESTS"] = False
        tc.variables["DILIGENT_BUILD_TOOLS_TESTS"] = False
        tc.variables["DILIGENT_BUILD_TOOLS_INCLUDE_TEST"] = False
        tc.variables["DILIGENT_NO_RENDER_STATE_PACKAGER"] = not self.options.with_render_state_packager
        tc.variables["ARCHIVER_SUPPORTED"] = not self.options.with_archiver
        tc.variables["DILIGENT_CLANG_COMPILE_OPTIONS"] = ""
        tc.variables["DILIGENT_MSVC_COMPILE_OPTIONS"] = ""
        tc.variables["ENABLE_RTTI"] = True
        tc.variables["ENABLE_EXCEPTIONS"] = True
        platform = self._diligent_platform()
        tc.variables[platform] = True
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def layout(self):
        cmake_layout(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

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
        self.requires("zlib/1.2.13")

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
        raise ConanInvalidConfiguration("Can't build for {}".format(self.settings.os))

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
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
