from conan import ConanFile, tools
from conans import CMake
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.43.0"


class EnjinCppSdk(ConanFile):
    name = "enjincppsdk"
    description = "A C++ SDK for development on the Enjin blockchain platform."
    license = "Apache-2.0"
    topics = ("enjin", "sdk", "blockchain")
    homepage = "https://github.com/enjin/enjin-cpp-sdk"
    url = "https://github.com/conan-io/conan-center-index"

    settings = "os", "compiler", "arch", "build_type"
    generators = "cmake", "cmake_find_package", "cmake_find_package_multi"

    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_default_http_client": [True, False],
        "with_default_ws_client": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_default_http_client": False,
        "with_default_ws_client": False,
    }

    _cmake = None
    short_paths = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    @property
    def _minimum_compilers_version(self):
        return {
            "Visual Studio": "16",
            "gcc": "9",
            "clang": "10",
        }

    def export_sources(self):
        self.copy("CMakeLists.txt")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

        if self.options.with_default_http_client:
            self.options["cpp-httplib"].with_openssl = True

        self.options["spdlog"].header_only = True

    def requirements(self):
        if self.options.with_default_http_client:
            self.requires("cpp-httplib/0.8.5")

        if self.options.with_default_ws_client:
            self.requires("ixwebsocket/11.0.4")

        self.requires("rapidjson/1.1.0")
        self.requires("spdlog/1.8.2")

    def build_requirements(self):
        self.build_requires("cmake/3.16.9")

    def validate(self):
        # Validations for OS
        if self.settings.os == "Macos":
            raise ConanInvalidConfiguration("macOS is not supported at this time. Contributions are welcomed.")

        # Validations for minimum required C++ standard
        compiler = self.settings.compiler

        if compiler.get_safe("cppstd"):
            tools.build.check_min_cppstd(self, self, 17)

        minimum_version = self._minimum_compilers_version.get(str(compiler), False)
        if not minimum_version:
            self.output.warn("C++17 support is required. Your compiler is unknown. Assuming it supports C++17.")
        elif tools.scm.Version(self, compiler.version) < minimum_version:
            raise ConanInvalidConfiguration("C++17 support is required, which your compiler does not support.")

        if compiler == "clang" and compiler.libcxx != "libstdc++11":
            raise ConanInvalidConfiguration("libstdc++11 is required for clang.")

        # Validations for dependencies
        if not self.options["spdlog"].header_only:
            raise ConanInvalidConfiguration(f"{self.name} requires spdlog:header_only=True to be enabled.")

        if self.options.with_default_http_client and not self.options["cpp-httplib"].with_openssl:
            raise ConanInvalidConfiguration(f"{self.name} requires cpp-httplib:with_openssl=True when using "
                                            f"with_default_http_client=True.")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version], destination=self._source_subfolder, strip_root=True)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake

        self._cmake = CMake(self)
        self._cmake.definitions["ENJINSDK_BUILD_SHARED"] = self.options.shared
        self._cmake.definitions["ENJINSDK_BUILD_TESTS"] = False
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE*", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "enjinsdk"))

    def package_info(self):
        self.cpp_info.set_property("cmake_target_name", "enjinsdk::enjinsdk")
        self.cpp_info.names["cmake_find_package"] = "enjinsdk"
        self.cpp_info.names["cmake_find_package_multi"] = "enjinsdk"
        self.cpp_info.libs = ["enjinsdk"]
