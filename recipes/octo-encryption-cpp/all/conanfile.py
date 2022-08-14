from conans import ConanFile, CMake
from conan.tools.files import get, collect_libs


class OctoEncryptionCPPConan(ConanFile):
    name = "octo-encryption-cpp"
    license = "MIT"
    url = "https://github.com/ofiriluz/octo-encryption-cpp"
    homepage = "https://github.com/ofiriluz/octo-encryption-cpp"
    description = "Octo encryption library"
    topics = ("cryptography", "cpp")
    generators = "cmake"
    settings = "os", "compiler", "build_type", "arch"

    @property
    def _source_subfolder(self):
        return "source"

    @property
    def _build_subfolder(self):
        return "build"

    def source(self):
        get(self, **self.conan_data["sources"][str(self.version)], strip_root=True, destination=self._source_subfolder)

    def requirements(self):
        self.requires("catch2/3.1.0")
        self.requires("openssl/3.0.5")

    def build(self):
        cmake = CMake(self)
        cmake.configure(source_folder=self._source_subfolder, build_folder=self._build_subfolder)
        cmake.build(build_dir=self._build_subfolder)
        cmake.test(build_dir=self._build_subfolder)

    def package(self):
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")
        cmake = CMake(self)
        cmake.configure(source_folder=self._source_subfolder, build_folder=self._build_subfolder)
        cmake.install(build_dir=self._build_subfolder)

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "octo-encryption-cpp")
        self.cpp_info.set_property("cmake_target_name", "octo-encryption-cpp::octo-encryption-cpp")
        self.cpp_info.set_property("pkg_config_name", "octo-encryption-cpp")
        self.cpp_info.components["octo-encryption-cpp"].libs = ["octo-encryption-cpp"]
        self.cpp_info.components["octo-encryption-cpp"].requires = [
            "catch2::catch2",
            "openssl::openssl"
        ]
        self.cpp_info.filenames["cmake_find_package"] = "octo-encryption-cpp"
        self.cpp_info.filenames["cmake_find_package_multi"] = "octo-encryption-cpp"
        self.cpp_info.names["cmake_find_package"] = "octo-encryption-cpp"
        self.cpp_info.names["cmake_find_package_multi"] = "octo-encryption-cpp"
        self.cpp_info.names["pkg_config"] = "octo-encryption-cpp"
        self.cpp_info.components["octo-encryption-cpp"].names["cmake_find_package"] = "octo-encryption-cpp"
        self.cpp_info.components["octo-encryption-cpp"].names["cmake_find_package_multi"] = "octo-encryption-cpp"
        self.cpp_info.components["octo-encryption-cpp"].set_property("cmake_target_name", "octo-encryption-cpp::octo-encryption-cpp")
        self.cpp_info.components["octo-encryption-cpp"].set_property("pkg_config_name", "octo-encryption-cpp")
