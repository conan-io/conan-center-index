from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.32.0"


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
        "with_spirv_tools": [True, False],
        "tools": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_spirv_tools": True,
        "tools": True
    }

    exports_sources = ["CMakeLists.txt", "patches/**"]
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

    def requirements(self):
        self.requires("cereal/1.3.0")
        self.requires("glslang/8.13.3559")
        self.requires("spirv-cross/{}".format(self._spirv_cross_version))
        self.requires("vulkan-headers/{}".format(self._vulkan_headers_version))
        if self.options.with_spirv_tools:
            self.requires("spirv-tools/v2020.5")
        if tools.Version(self.version) < "1.1.0":
            raise ConanInvalidConfiguration("MoltenVK < 1.1.0 requires vulkan-portability")

    @property
    def _spirv_cross_version(self):
        return {
            "1.1.1": "20210115", # can't compile with spirv-cross < 20210115
            "1.1.0": "20200917", # works with spirv-cross 20200917 only
        }.get(self.version)

    @property
    def _vulkan_headers_version(self):
        return {
            "1.1.1": "1.2.162.0",
            "1.1.0": "1.2.154.0",
            "1.0.44": "1.2.148.0",
            "1.0.43": "1.2.141.0",
            "1.0.42": "1.2.141.0",
            "1.0.41": "1.2.135.0",
            "1.0.40": "1.2.131.1",
            "1.0.39": "1.1.130.0",
            "1.0.38": "1.1.126.0",
            "1.0.37": "1.1.121.0",
            "1.0.36": "1.1.114.0",
            "1.0.35": "1.1.108.0",
            "1.0.34": "1.1.106.0",
            "1.0.33": "1.1.101.0",
            "1.0.32": "1.1.97.0",
            "1.0.31": "1.1.97.0",
            "1.0.30": "1.1.92.0",
            "1.0.29": "1.1.92.0",
            "1.0.28": "1.1.92.0",
            "1.0.27": "1.1.92.0",
            "1.0.26": "1.1.85.0",
            "1.0.25": "1.1.85.0",
            "1.0.24": "1.1.85.0",
            "1.0.23": "1.1.85.0",
            "1.0.22": "1.1.82.0",
            "1.0.21": "1.1.82.0",
            "1.0.20": "1.1.82.0",
            "1.0.19": "1.1.82.0",
            "1.0.18": "1.1.82.0",
            "1.0.17": "1.1.82.0",
        }.get(self.version)

    def package_id(self):
        # MoltenVK >=1.42 requires at least XCode 12.0 (11.4 actually) at build
        # time but can be consumed by older compiler versions
        if tools.Version(self.version) >= "1.0.42":
            if tools.Version(self.settings.compiler.version) < "12.0":
                compatible_pkg = self.info.clone()
                compatible_pkg.settings.compiler.version = "12.0"
                self.compatible_packages.append(compatible_pkg)

    def validate(self):
        if tools.Version(self.version) >= "1.0.42":
            if tools.Version(self.settings.compiler.version) < "12.0":
                raise ConanInvalidConfiguration("MoltenVK {} requires XCode 12.0 or higher at build time".format(self.version))

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("MoltenVK-" + self.version, self._source_subfolder)

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        if tools.Version(self.version) >= "1.1.0":
            tools.replace_in_file(os.path.join(self._source_subfolder, "MoltenVK", "MoltenVK", "GPUObjects", "MVKDevice.mm"),
                                  "#include \"mvkGitRevDerived.h\"",
                                  "static const char* mvkRevString = \"{}\";".format(self._mvk_commit_hash))

    @property
    def _mvk_commit_hash(self):
        return {
            "1.1.1": "49de6604b0395057e7d3b7ce7001ed29b25708f7",
            "1.1.0": "b9b78def172074872bfbb1015ccf75eeec554ae2",
        }.get(self.version)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["MVK_VERSION"] = self.version
        self._cmake.definitions["MVK_WITH_SPIRV_TOOLS"] = self.options.with_spirv_tools
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
