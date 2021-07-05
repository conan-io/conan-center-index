from conans import ConanFile, CMake, tools
import os

required_conan_version = ">=1.33.0"


class LibaecConan(ConanFile):
    name = "libaec"
    license = "BSD-2-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://gitlab.dkrz.de/k202009/libaec"
    description = "Adaptive Entropy Coding library"
    topics = ("conan", "dsp", "libaec", "encoding", "decoding")
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    generators = "cmake"
    exports_sources = ["CMakeLists.txt", "patches/*"]

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
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.configure(build_folder=self._build_subfolder)
        return cmake

    def build(self):
        tools.patch(**self.conan_data["patches"][self.version])
        tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"), "add_subdirectory(tests)", "")
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="Copyright.txt", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, 'share'))

    def package_info(self):
        if self.settings.os == "Windows" and self.options.shared:
            self.cpp_info.libs = ["szip", "aec"]
        else:
            self.cpp_info.libs = ["sz", "aec"]
