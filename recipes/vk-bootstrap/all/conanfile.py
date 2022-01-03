from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration

required_conan_version = ">=1.33.0"


class VkBootstrapConan(ConanFile):
    name = "vk-bootstrap"
    description = "Vulkan bootstraping library."
    license = "MIT"
    topics = ("vk-bootstrap", "vulkan")
    homepage = "https://github.com/charles-lunarg/vk-bootstrap"
    url = "https://github.com/conan-io/conan-center-index"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    generators = "cmake"
    _cmake = None

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

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        self.requires("vulkan-headers/1.2.184")

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "5",
            "Visual Studio": "15",
            "clang": "3.7" if tools.stdcpp_library(self) == "stdc++" else "6",
            "apple-clang": "10",
        }

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, 14)

        def lazy_lt_semver(v1, v2):
            lv1 = [int(v) for v in v1.split(".")]
            lv2 = [int(v) for v in v2.split(".")]
            min_length = min(len(lv1), len(lv2))
            return lv1[:min_length] < lv2[:min_length]

        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if not minimum_version:
            self.output.warn("vk-bootstrap requires C++14. Your compiler is unknown. Assuming it supports C++14.")
        elif lazy_lt_semver(str(self.settings.compiler.version), minimum_version):
            raise ConanInvalidConfiguration("vk-bootstrap requires C++14, which your compiler does not support.")

        if self.settings.compiler == "Visual Studio" and self.options.shared:
            raise ConanInvalidConfiguration("vk-boostrap shared not supported with Visual Studio")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["VK_BOOTSTRAP_TEST"] = False
        if tools.Version(self.version) >= "0.3.0":
            self._cmake.definitions["VK_BOOTSTRAP_VULKAN_HEADER_DIR"] = ";".join(self.deps_cpp_info["vulkan-headers"].include_paths)
        if tools.Version(self.version) >= "0.4.0":
            self._cmake.definitions["VK_BOOTSTRAP_WERROR"] = False
        self._cmake.configure()
        return self._cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE.txt", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["vk-bootstrap"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["dl"]
