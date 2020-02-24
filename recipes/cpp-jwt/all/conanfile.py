from conans import ConanFile, tools, CMake
import os


class CppJwtConan(ConanFile):
    name = "cpp-jwt"
    homepage = "https://github.com/arun11299/cpp-jwt"
    description = "A C++ library for handling JWT tokens"
    topics = ("jwt", "javascript", "auth", "header-only")
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "compiler", "arch", "build_type"
    generators = "cmake", "cmake_find_package"
    exports_sources = ["CMakeLists.txt"]
    license = "MIT"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def requirements(self):
        self.requires("openssl/1.0.2t")
        self.requires("nlohmann_json/3.7.3")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["CPP_JWT_BUILD_EXAMPLES"] = False
        cmake.definitions["CPP_JWT_BUILD_TESTS"] = False
        cmake.definitions["CPP_JWT_USE_VENDORED_NLOHMANN_JSON"] = False
        cmake.configure(source_folder=self._source_subfolder)
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE*", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib"))

    def package_id(self):
        self.info.header_only()
