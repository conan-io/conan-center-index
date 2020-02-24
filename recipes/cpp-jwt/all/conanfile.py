from conans import ConanFile, tools, CMake
import os
from conans.errors import ConanInvalidConfiguration


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

    def configure(self):
        minimal_cpp_standard = "14"
        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, minimal_cpp_standard)

        minimal_version = {
            "gcc": "6.4",
            "clang": "5",
            "apple-clang", "10"
        }

        compiler = str(self.settings.compiler)
        if compiler not in minimal_version:
            self.output.warn(
                "%s recipe lacks information about the %s compiler standard version support" % (self.name, compiler))
            self.output.warn(
                "%s requires a compiler that supports at least C++%s" % (self.name, minimal_cpp_standard))
            return

        version = tools.Version(self.settings.compiler.version)
        if version < minimal_version[compiler]:
            raise ConanInvalidConfiguration(
                "%s requires a compiler that supports at least C++%s" % (self.name, minimal_cpp_standard))

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
