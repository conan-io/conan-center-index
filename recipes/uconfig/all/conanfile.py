from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration

import os

required_conan_version = ">=1.33.0"


class UconfigConan(ConanFile):
    name = "uconfig"
    description = "Lightweight, header-only, C++17 configuration library"
    topics = ("conan", "configuration", "env", "json")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/TinkoffCreditSystems/uconfig"
    license = "Apache-2.0"

    generators = "cmake", "cmake_find_package_multi"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "with_rapidjson": [True, False],
    }
    default_options = {
        "with_rapidjson": True,
    }

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        if tools.Version(self.version) < "2.0.2":
            self._cmake.definitions["UCONFIG_BUNDLED_MODE"] = False
            self._cmake.definitions["BUILD_TESTING"] = False
        else:
            self._cmake.definitions["UCONFIG_BUILD_TESTING"] = False
        self._cmake.configure(source_folder=self._source_subfolder, build_folder=self._build_subfolder)
        return self._cmake

    def requirements(self):
        if self.options.with_rapidjson:
            self.requires("rapidjson/1.1.0")

    def configure(self):
        compiler = str(self.settings.compiler)
        compiler_version = tools.Version(self.settings.compiler.version)

        min_req_cppstd = "17"
        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, min_req_cppstd)
        else:
            self.output.warn("%s recipe lacks information about the %s compiler"
                             " standard version support." % (self.name, compiler))

        minimal_version = {
            "Visual Studio": "16",
            "gcc": "7.3",
            "clang": "6.0",
            "apple-clang": "10.0",
        }
        # Exclude not supported compilers
        if compiler not in minimal_version:
            self.output.info("%s requires a compiler that supports at least C++%s" % (self.name, min_req_cppstd))
            return
        if compiler_version < minimal_version[compiler]:
            raise ConanInvalidConfiguration(
                "%s requires a compiler that supports at least C++%s. %s %s is not supported." %
                (self.name, min_req_cppstd, compiler, compiler_version))

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], destination=self._source_subfolder, strip_root=True)

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        if self.options.with_rapidjson:
            self.cpp_info.defines = ["RAPIDJSON_HAS_STDSTRING=1"]

    def package_id(self):
        self.info.header_only()
