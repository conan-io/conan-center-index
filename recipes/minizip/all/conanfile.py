from conans import ConanFile, CMake, tools
import os


class MinizipConan(ConanFile):
    name = "minizip"
    description = "minizip is a zip manipulation library written in C that is supported on Windows, macOS, and Linux."
    topics = ("conan", "minizip", "compression")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/nmoinvaz/minizip"
    license = "Zlib"
    exports_sources = ["CMakeLists.txt", "patches/*"]
    generators = "cmake_find_package"

    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"
    _cmake = None

    requires = (
        "zlib/1.2.11",
        "zstd/1.4.5",
        "bzip2/1.0.8",
    )

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd
        
    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        if not self._cmake:
            self._cmake = CMake(self)
            self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        tools.patch(**self.conan_data["patches"][self.version], base_path=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        # If the CMakeLists.txt has a proper install method, the steps below may be redundant
        # If so, you can just remove the lines below
        #include_folder = os.path.join(self._source_subfolder, "include")
        #self.copy(pattern="*", dst="include", src=include_folder)
        #self.copy(pattern="*.dll", dst="bin", keep_path=False)
        #self.copy(pattern="*.lib", dst="lib", keep_path=False)
        #self.copy(pattern="*.a", dst="lib", keep_path=False)
        #self.copy(pattern="*.so*", dst="lib", keep_path=False)
        #self.copy(pattern="*.dylib", dst="lib", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
