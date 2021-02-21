from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os


class MoltenVKConan(ConanFile):
    name = "moltenvk"
    description = "MoltenVK is a Vulkan Portability implementation. It " \
                  "layers a subset of the high-performance, industry-standard " \
                  "Vulkan graphics and compute API over Apple's Metal " \
                  "graphics framework, enabling Vulkan applications to run " \
                  "on iOS and macOS. "
    license = "Apache-2.0"
    topics = ("conan", "moltenvk", "khronos", "vulkan", "metal")
    homepage = "https://github.com/KhronosGroup/MoltenVK"
    url = "https://github.com/conan-io/conan-center-index"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "tools": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "tools": True
    }

    exports_sources = "CMakeLists.txt"
    generators = "cmake"
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, 11)
        if self.settings.os not in ["Macos", "iOS", "tvOS"]:
            raise ConanInvalidConfiguration("MoltenVK only supported on MacOS, iOS and tvOS")
        # Might depend on MoltenVK version
        if tools.Version(self.settings.compiler.version) < 11:
            raise ConanInvalidConfiguration("MoltenVK {} requires macos-sdk 10.15+ (XCode 11 or higher)".format(self.version))

    def requirements(self):
        self.requires("cereal/1.3.0")
        self.requires("glslang/8.13.3559")
        self.requires("spirv-cross/20210115")
        self.requires("spirv-tools/v2020.5")
        self.requires("vulkan-headers/1.2.162.0")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("MoltenVK-" + self.version, self._source_subfolder)

    def _patch_sources(self):
        # Note: All these fixes might be very specific to 1.1.1
        # Properly include external spirv-cross headers
        files_to_patch = [
            os.path.join(self._source_subfolder, "MoltenVK", "MoltenVK", "GPUObjects", "MVKPixelFormats.h"),
            os.path.join(self._source_subfolder, "MoltenVKShaderConverter", "Common", "SPIRVSupport.cpp"),
            os.path.join(self._source_subfolder, "MoltenVKShaderConverter", "MoltenVKShaderConverter", "SPIRVReflection.h"),
            os.path.join(self._source_subfolder, "MoltenVKShaderConverter", "MoltenVKShaderConverter", "SPIRVToMSLConverter.h")
        ]
        for file_to_patch in files_to_patch:
            tools.replace_in_file(file_to_patch, "SPIRV-Cross", "spirv_cross")
        # Provide a random spirv-cross hash
        tools.replace_in_file(os.path.join(self._source_subfolder, "MoltenVK", "MoltenVK", "GPUObjects", "MVKDevice.mm"),
                              "#include \"mvkGitRevDerived.h\"",
                              "static const char* mvkRevString = \"fc0750d67cfe825b887dd2cf25a42e9d9a013eb2\";")

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["MVK_BUILD_SHADERCONVERTER_TOOL"] = self.options.tools
        self._cmake.configure()
        return self._cmake

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["MoltenVK"]
        self.cpp_info.frameworks = ["Metal", "Foundation", "QuartzCore", "AppKit", "IOSurface"]
        if self.settings.os == "Macos":
            self.cpp_info.frameworks.append("IOKit")
        elif self.settings.os in ["iOS", "tvOS"]:
            self.cpp_info.frameworks.append("UIKit")

        if self.options.tools:
            bin_path = os.path.join(self.package_folder, "bin")
            self.output.info("Appending PATH environment variable: {}".format(bin_path))
            self.env_info.PATH.append(bin_path)
