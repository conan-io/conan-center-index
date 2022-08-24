from conan import ConanFile, tools
from conans import CMake
from conan.errors import ConanInvalidConfiguration

required_conan_version = ">=1.33.0"


class JxrlibConan(ConanFile):
    name = "jxrlib"
    description = "jxrlib is JPEG XR Image Codec reference implementation library released by Microsoft under BSD-2-Clause License."
    homepage = "https://jxrlib.codeplex.com/"
    url = "https://github.com/conan-io/conan-center-index"
    license = "BSD-2-Clause"
    topics = ("conan", "jxr", "jpeg", "xr")
    exports_sources = ["CMakeLists.txt", "patches/**"]
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def validate(self):
        if self.settings.compiler == "Visual Studio" and self.options.shared:
            raise ConanInvalidConfiguration("jxrlib shared not supported by Visual Studio")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.configure(build_dir=self._build_subfolder)
        return self._cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.patch(self, **patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)

    def package_info(self):
        self.cpp_info.libs = ["jxrglue", "jpegxr"]

        if self.settings.os == "Linux":
            self.cpp_info.system_libs.append("m")
        if self.settings.os != "Windows":
            self.cpp_info.defines.append("__ANSI__")

        self.cpp_info.names["pkg_config"] = "libjxr"
        self.cpp_info.names["cmake_find_package"] = "JXR"
        self.cpp_info.names["cmake_find_package_multi"] = "JXR"
