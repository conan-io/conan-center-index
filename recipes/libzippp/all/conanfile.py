from conans import ConanFile, CMake, tools
import os


class LibZipppConan(ConanFile):
    name = "libzippp"
    description = "A simple basic C++ wrapper around the libzip library"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/ctabin/libzippp"
    license = "BSD-3-Clause"
    topics = ("conan", "zip", "libzippp", "zip-archives", "zip-editing")
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake", "cmake_find_package_multi"
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_encryption": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_encryption": False
    }
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        self.requires("libzip/1.7.3")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        # eg. 'libzippp-libzippp-v4.0-1.7.3'
        extracted_dir = self.name + "-" + self.name + "-v" + self.version + \
            "-" + self.deps_cpp_info["libzip"].version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["LIBZIPPP_INSTALL"] = True
        self._cmake.definitions["LIBZIPPP_INSTALL_HEADERS"] = True
        self._cmake.definitions["LIBZIPPP_ENABLE_ENCRYPTION"] = self.options.with_encryption
        self._cmake.configure()
        return self._cmake

    def _patch_source(self):
        tools.replace_in_file('source_subfolder/CMakeLists.txt',
                              'find_package(LIBZIP MODULE REQUIRED)',
                              'find_package(libzip REQUIRED CONFIG)')

    def build(self):
        self._patch_source()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        self.copy(pattern="LICENCE", dst="licenses", src=self._source_subfolder)
        tools.rmdir(os.path.join(self.package_folder, "share"))
        tools.rmdir(os.path.join(self.package_folder, "cmake"))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.names["cmake_find_package"] = "libzippp"
        self.cpp_info.names["cmake_find_package_multi"] = "libzippp"
        if self.options.with_encryption:
            self.cpp_info.defines.append("LIBZIPPP_WITH_ENCRYPTION")
