from conans import ConanFile, CMake, tools
import os


class OggConan(ConanFile):
    name = "ogg"
    description = "The OGG library"
    topics = ("conan", "ogg", "codec", "audio", "lossless")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/xiph/ogg"
    license = "BSD-2-Clause"
    exports_sources = ["CMakeLists.txt", "patches/*"]
    generators = "cmake"

    settings = "os", "arch", "build_type", "compiler"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

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
        cmake = CMake(self)
        cmake.configure(build_folder=self._build_subfolder)
        return cmake

    def build(self):
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("COPYING", src=self._source_subfolder, dst="licenses", keep_path=False)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.filenames["cmake_find_package"] = "Ogg"
        self.cpp_info.filenames["cmake_find_package_multi"] = "Ogg"
        self.cpp_info.names["cmake_find_package"] = "Ogg"
        self.cpp_info.names["cmake_find_package_multi"] = "Ogg"
        self.cpp_info.components["libogg"].libs = ["ogg"]
        self.cpp_info.components["libogg"].names["cmake_find_package"] = "ogg"
        self.cpp_info.components["libogg"].names["cmake_find_package_multi"] = "ogg"
