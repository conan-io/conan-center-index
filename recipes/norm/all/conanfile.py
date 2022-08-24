from conan import ConanFile, tools
from conans import CMake
import os


class NormConan(ConanFile):
    name = "norm"
    description = "A reliable multicast transport protocol"
    topics = ("norm", "multicast", "transport protocol", "nack-oriented reliable multicast")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.nrl.navy.mil/itd/ncs/products/norm"
    exports_sources = "CMakeLists.txt", "patches/**"
    generators = "cmake"
    license = "NRL"
    settings = "os", "compiler", "build_type", "arch"
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

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version], destination=self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["NORM_CUSTOM_PROTOLIB_VERSION"] = "./protolib" # FIXME: use external protolib when available in CCI
        self._cmake.configure()
        return self._cmake

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.patch(self, **patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        if self.options.shared:
            tools.remove_files_by_mask(os.path.join(self.package_folder, "lib"), "*proto*")

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "norm"
        self.cpp_info.names["cmake_find_package_multi"] = "norm"
        self.cpp_info.libs = ["norm"]
        if not self.options.shared:
            self.cpp_info.libs.append("protokit")

        if self.settings.os == "Windows" and self.options.shared:
            self.cpp_info.defines.append("NORM_USE_DLL")

        if self.settings.os == "Windows":
            self.cpp_info.system_libs = [
                "ws2_32", "iphlpapi", "user32", "gdi32", "Advapi32", "ntdll"]
        elif self.settings.os == "Linux":
            self.cpp_info.system_libs = ["dl", "rt"]
            
        if self.settings.os == "Linux" or self.settings.os == "FreeBSD":
            self.cpp_info.system_libs.append("pthread")
