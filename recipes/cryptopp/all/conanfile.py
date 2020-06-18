from conans import ConanFile, CMake, tools
import os
import shutil


class CryptoPPConan(ConanFile):
    name = "cryptopp"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/weidai11/cryptopp"
    license = "BSL-1.0"
    description = "Crypto++ Library is a free C++ class library of cryptographic schemes."
    topics = ("conan", "cryptopp", "crypto", "cryptographic", "security")
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {'shared': False, 'fPIC': True}
    generators = "cmake"
    exports_sources = ["CMakeLists.txt", "patches/**"]
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        archive_file = 'CRYPTOPP_%s' % self.version.replace('.', '_')
        os.rename("cryptopp-%s" % archive_file, self._source_subfolder)
        tools.download("https://raw.githubusercontent.com/noloader/cryptopp-cmake/702bb894f6636e71278d822f01a530397f78966e/CMakeLists.txt",
                       os.path.join(self._source_subfolder, "CMakeLists.txt"),
                       sha256="e2268878bc3b779334dd57515d7656f0567b879a6c8dcfb876cabbe72dccbac1")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["BUILD_STATIC"] = not self.options.shared
        self._cmake.definitions["BUILD_SHARED"] = self.options.shared
        self._cmake.definitions["BUILD_TESTING"] = False
        self._cmake.definitions["BUILD_DOCUMENTATION"] = False
        if self.settings.os == 'Android':
            self._cmake.definitions["CRYPTOPP_NATIVE_ARCH"] = True
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        if self.settings.os == 'Android' and 'ANDROID_NDK_HOME' in os.environ:
            shutil.copyfile(os.path.join(tools.get_env('ANDROID_NDK_HOME'), 'sources', 'android', 'cpufeatures', 'cpu-features.h'),
                            os.path.join(self._source_subfolder, "cpu-features.h"))
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="License.txt", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os == "Linux":
            self.cpp_info.system_libs = ["pthread", "m"]
