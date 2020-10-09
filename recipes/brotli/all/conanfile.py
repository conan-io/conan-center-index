from conans import CMake, ConanFile, tools
import os


class BrotliConan(ConanFile):
    name = "brotli"
    description = "Brotli compression format"
    topics = ("conan", "brotli", "compression")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/google/brotli"
    license = "MIT",
    exports_sources = ["CMakeLists.txt", "patches/*"]
    generators = "cmake",
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
        del self.settings.compiler.cppstd
        del self.settings.compiler.libcxx

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_folder = "brotli-{}".format(self.version)
        os.rename(extracted_folder, self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["BROTLI_BUNDLED_MODE"] = False
        self._cmake.definitions["BROTLI_DISABLE_TESTS"] = True
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "Brotli"
        self.cpp_info.names["cmake_find_package_multi"] = "Brotli"
        includedir = os.path.join("include", "brotli")
        # brotlicommon
        self.cpp_info.components["brotlicommon"].names["pkg_config"] = "libbrotlicommon"
        self.cpp_info.components["brotlicommon"].includedirs.append(includedir)
        self.cpp_info.components["brotlicommon"].libs = [self._get_decorated_lib("brotlicommon")]
        if self.settings.os == "Windows" and self.options.shared:
            self.cpp_info.components["brotlicommon"].defines.append("BROTLI_SHARED_COMPILATION")
        # brotlidec
        self.cpp_info.components["brotlidec"].names["pkg_config"] = "libbrotlidec"
        self.cpp_info.components["brotlidec"].includedirs.append(includedir)
        self.cpp_info.components["brotlidec"].libs = [self._get_decorated_lib("brotlidec")]
        self.cpp_info.components["brotlidec"].requires = ["brotlicommon"]
        # brotlienc
        self.cpp_info.components["brotlienc"].names["pkg_config"] = "libbrotlienc"
        self.cpp_info.components["brotlienc"].includedirs.append(includedir)
        self.cpp_info.components["brotlienc"].libs = [self._get_decorated_lib("brotlienc")]
        self.cpp_info.components["brotlienc"].requires = ["brotlicommon"]
        if self.settings.os == "Linux":
            self.cpp_info.components["brotlienc"].system_libs = ["m"]

    def _get_decorated_lib(self, name):
        libname = name
        if not self.options.shared:
            libname += "-static"
        return libname
