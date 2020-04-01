from conans import ConanFile, CMake, tools
import os


class EnetConan(ConanFile):
    name = "enet"
    description = "ENet reliable UDP networking library"
    topics = ("conan", "enet", "udp", "networking")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/lsalzman/enet"
    license = "MIT"
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake"

    settings = "os", "arch", "compiler", "build_type"

    _source_subfolder = "source_subfolder"

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        include_folder = os.path.join(self._source_subfolder, "include")
        self.copy(pattern="*", dst="include", src=include_folder)
        self.copy(pattern="*.lib", dst="lib", src="lib", keep_path=False)
        self.copy(pattern="*.a", dst="lib", src="lib", keep_path=False)
        self.copy(pattern="*.dylib", dst="lib", src="lib", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.compiler == "Visual Studio":
            self.cpp_info.system_libs.extend(["ws2_32", "winmm"])
