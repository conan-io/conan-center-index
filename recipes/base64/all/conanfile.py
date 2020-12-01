import os
from conans import ConanFile, CMake, tools


class CppcodecConan(ConanFile):
    name = "base64"
    license = "BSD-2-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/aklomp/base64"
    description = "Fast Base64 stream encoder/decoder"
    topics = ("base64", "codec")
    exports_sources = ["CMakeLists.txt", "cmake/*", "test/*"]
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "fPIC": [True, False],
    }
    default_options = {
        "fPIC": True,
    }

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC
        del self.settings.compiler.cppstd
        del self.settings.compiler.libcxx

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)
        os.rename("CMakeLists.txt", os.path.join(self._source_subfolder, "CMakeLists.txt"))
        os.rename("cmake", os.path.join(self._source_subfolder, "cmake"))
        os.rename(os.path.join("test", "CMakeLists.txt"), os.path.join(self._source_subfolder, "test", "CMakeLists.txt"))

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.configure(source_folder=self._source_subfolder, build_folder=self._build_subfolder)
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build(target=self.name)

    def package(self):
        self.copy(pattern="*.h", dst="include", src=os.path.join(self._source_subfolder, "include"))
        self.copy(pattern="*.a", dst="lib", keep_path=False)
        self.copy(pattern="*.lib", dst="lib", keep_path=False)
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)

    def package_info(self):
        self.cpp_info.libs = [self.name]
