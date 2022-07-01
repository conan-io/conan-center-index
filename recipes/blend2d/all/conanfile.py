from conans import ConanFile, CMake, tools
import os

required_conan_version = ">=1.33.0"

class Blend2dConan(ConanFile):
    name = "blend2d"
    description = "2D Vector Graphics Engine Powered by a JIT Compiler"
    topics = ("2d-graphics", "rasterization", "asmjit", "jit")
    license = "Zlib"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://blend2d.com/"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }
    generators = "cmake", "cmake_find_package_multi"

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _is_msvc(self):
        return str(self.settings.compiler) in ["Visual Studio", "msvc"]

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
        self.requires("asmjit/cci.20220210")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, 11)

        # In Visual Studio < 16, there are compilation error. patch is already provided.
        # https://github.com/blend2d/blend2d/commit/63db360c7eb2c1c3ca9cd92a867dbb23dc95ca7d
        if self._is_msvc and tools.Version(self.settings.compiler.version) < "16":
            raise tools.ConanInvalidConfiguration("This recipe does not support this compiler version")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
            destination=self._source_subfolder, strip_root=True)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["BLEND2D_TEST"] = False
        self._cmake.definitions["BLEND2D_EMBED"] = False
        self._cmake.definitions["BLEND2D_STATIC"] = not self.options.shared
        self._cmake.definitions["BLEND2D_NO_STDCXX"] = False
        if not self.options.shared:
            self._cmake.definitions["CMAKE_C_FLAGS"] = "-DBL_STATIC"
            self._cmake.definitions["CMAKE_CXX_FLAGS"] = "-DBL_STATIC"
        self._cmake.configure()
        return self._cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE.md", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.libs = ["blend2d"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["pthread", "rt",])
        if not self.options.shared:
            self.cpp_info.defines.append("BL_STATIC")
