from conans import ConanFile, CMake, tools
import os


class JanssonConan(ConanFile):
    name = "jansson"
    description = "C library for encoding, decoding and manipulating JSON data"
    topics = ("conan", "jansson", "json", "encoding", "decoding", "manipulation")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://www.digip.org/jansson/"
    license = "MIT"
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "use_urandom": [True, False],
        "use_windows_cryptoapi": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "use_urandom": True,
        "use_windows_cryptoapi": True
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

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["JANSSON_BUILD_DOCS"] = False
        self._cmake.definitions["JANSSON_BUILD_SHARED_LIBS"] = self.options.shared
        self._cmake.definitions["JANSSON_EXAMPLES"] = False
        self._cmake.definitions["JANSSON_WITHOUT_TESTS"] = True
        self._cmake.definitions["USE_URANDOM"] = self.options.use_urandom
        self._cmake.definitions["USE_WINDOWS_CRYPTOAPI"] = self.options.use_windows_cryptoapi
        if self.settings.compiler == "Visual Studio":
            self._cmake.definitions["JANSSON_STATIC_CRT"] = str(self.settings.compiler.runtime).startswith("MT")
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        # drop pc and cmake file
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "cmake"))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
