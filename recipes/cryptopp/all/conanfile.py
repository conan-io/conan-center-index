from conans import ConanFile, CMake, tools
import os
import shutil


class CryptoPPConan(ConanFile):
    name = "cryptopp"
    version = ""
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/weidai11/cryptopp"
    license = "BSL-1.0"
    description = "Crypto++ Library is a free C++ class library of cryptographic schemes."
    topics = ("conan", "cryptopp", "crypto", "cryptographic", "security")
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {'shared': False, 'fPIC': True}
    generators = "cmake"
    exports_sources = ["CMakeLists.txt"]
    exports_sources = ["CMakeLists.txt", "CMakeLists.original.txt"]

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
        shutil.move("CMakeLists.original.txt", os.path.join(self._source_subfolder, "CMakeLists.txt"))

        if self.settings.os == 'Android' and 'ANDROID_NDK_HOME' in os.environ:
            shutil.copyfile(os.environ['ANDROID_NDK_HOME'] + '/sources/android/cpufeatures/cpu-features.h', os.path.join(self._source_subfolder, "cpu-features.h"))

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)

        if self.settings.os == "Windows":
            self._cmake.definitions["CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS"] = self.options.shared
        self._cmake.definitions["BUILD_STATIC"] = not self.options.shared
        self._cmake.definitions["BUILD_SHARED"] = self.options.shared
        self._cmake.definitions["BUILD_TESTING"] = False
        self._cmake.definitions["BUILD_DOCUMENTATION"] = False
        if self.settings.os == 'Android':
            self._cmake.definitions["CRYPTOPP_NATIVE_ARCH"] = True
        self._cmake.configure()
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="License.txt", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
