from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os


class MicrosoftGltfSdkConan(ConanFile):
    name = "ms-gltf-sdk"
    description = "A C++ Deserializer/Serializer for glTF"
    license = "MIT"
    topics = ("conan", "gltf-sdk", "gltf", "serializer", "deserializer")
    homepage = "https://github.com/microsoft/glTF-SDK"
    url = "https://github.com/conan-io/conan-center-index"

    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    exports_sources = ["CMakeLists.txt", "patches/**"]
    generators = "cmake"
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    @property
    def _minimum_compilers_version(self):
        return {
            "Visual Studio": "14",
            "gcc": "6",
            "clang": "5",
            "apple-clang": "5.1",
        }

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, 14)
        minimum_version = self._minimum_compilers_version.get(str(self.settings.compiler), False)
        if not minimum_version:
            self.output.warn("{} requires C++14. Your compiler is unknown. Assuming it supports C++14.".format(self.name))
        elif tools.Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration("{} requires C++14, which your compiler does not support.".format(self.name))
        if self.settings.compiler == "Visual Studio" and self.options.shared:
            raise ConanInvalidConfiguration("{} shared in not supported by Visual Studio".format(self.name))

    def requirements(self):
        self.requires("rapidjson/1.1.0")

    def build_requirements(self):
        if not (tools.which("pwsh") or tools.which("powershell")):
            self.build_requires("powershell/7.1.2")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("glTF-SDK-r" + self.version, self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["ENABLE_UNIT_TESTS"] = False
        self._cmake.definitions["ENABLE_SAMPLES"] = False
        self._cmake.configure()
        return self._cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["GLTFSDK"]
