from conans import CMake, ConanFile, tools
import os


class BrotliConan(ConanFile):
    name = "brotli"
    description = "Brotli compression format"
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
    _source_subfolder = "source_subfolder"

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
        cmake = CMake(self)
        cmake.definitions["BROTLI_BUNDLED_MODE"] = False
        cmake.definitions["BROTLI_DISABLE_TESTS"] = True
        cmake.configure()
        return cmake

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

    def _get_libraries(self, shared):
        libs = ["brotlienc", "brotlidec", "brotlicommon"]
        if not shared:
            libs = ["{}-static".format(l) for l in libs]
        return libs

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "Brotli"
        self.cpp_info.names["cmake_find_package_multi"] = "Brotli"
        self.cpp_info.libs = self._get_libraries(self.options.shared)
        self.cpp_info.includedirs = ["include", os.path.join("include", "brotli")]
        if self.options.shared:
            self.cpp_info.defines.append("BROTLI_SHARED_COMPILATION")
        if self.settings.os == "Linux":
            self.cpp_info.system_libs = ["m"]
