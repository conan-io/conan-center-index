from conans import ConanFile, tools, CMake
from conans.errors import ConanInvalidConfiguration
import os


class ZXingCppConan(ConanFile):
    name = "zxing-cpp"
    homepage = "https://github.com/nu-book/zxing-cpp"
    description = "c++14 port of ZXing, a barcode scanning library"
    topics = ("conan", "zxing", "barcode", "scanner", "generator")
    url = "https://github.com/conan-io/conan-center-index"
    license = "Apache-2.0"
    exports_sources = ["CMakeLists.txt"]
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "enable_encoders": [True, False],
        "enable_decoders": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "enable_encoders": True,
        "enable_decoders": True,
    }
    generators = "cmake"

    _cmake = None
    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    _compiler_cpp14_support = {
        "gcc": "5",
        "Visual Studio": "14",
        "clang": "3.4",
        "apple-clang": "3.4",
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

        if str(self.settings.compiler.cppstd) in ("98", "gnu98", "11", "gnu11"):
            raise ConanInvalidConfiguration("This library requires at least c++ 14. The requested c++ standard is too low.")
        try:
            minimum_required_version = self._compiler_cpp14_support[str(self.settings.compiler)]
            if self.settings.compiler.version < tools.Version(minimum_required_version):
                raise ConanInvalidConfiguration("This compiler is too old. This library needs a compiler with c++14 support")
        except KeyError:
            raise ConanInvalidConfiguration("This recipe does not support this compiler. Consider adding it.")

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("zxing-cpp-{}".format(self.version), self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["ENABLE_ENCODERS"] = self.options.enable_encoders
        self._cmake.definitions["ENABLE_DECODERS"] = self.options.enable_decoders
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE*", src=self._source_subfolder, dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()

        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "ZXing"
        self.cpp_info.names["cmake_find_package_multi"] = "ZXing"
        self.cpp_info.names["pkg_config"] = "zxing"
        self.cpp_info.libs = ["ZXingCore"]
        self.cpp_info.includedirs = ["include", os.path.join("include", "ZXing")]
