import os
from conan import ConanFile, tools
from conans import CMake

class EnkiTSConan(ConanFile):
    name = "enkits"
    description = "A permissively licensed C and C++ Task Scheduler for creating parallel programs."
    topics = ("conan", "c", "thread", "multithreading", "scheduling", "enkits", "gamedev")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/dougbinks/enkiTS"
    license = "Zlib"
    settings = "os", "arch", "compiler", "build_type"

    exports_sources = "CMakeLists.txt", "patches/*"
    generators = "cmake"

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

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version])
        extracted_dir = "enkiTS-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        if not self._cmake:
            self._cmake = CMake(self)
            self._cmake.definitions["ENKITS_INSTALL"] = True
            self._cmake.definitions["ENKITS_BUILD_EXAMPLES"] = False
            self._cmake.definitions["ENKITS_BUILD_SHARED"] = self.options.shared
            self._cmake.configure()
        return self._cmake

    def build(self):
        for patch in self.conan_data["patches"][self.version]:
            tools.files.patch(self, **patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="License.txt", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["enkiTS"]
        
        if self.options.shared:
            self.cpp_info.defines.append("ENKITS_DLL=1")
        if self.settings.os == "Linux":
            self.cpp_info.system_libs = ["pthread"]
