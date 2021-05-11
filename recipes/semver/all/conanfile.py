from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration

import os

required_conan_version = ">=1.33.0"


class SemverConan(ConanFile):
    name = "semver"
    description = "Semantic Versioning for modern C++"
    topics = ("conan", "semver", "semantic", "versioning")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/Neargye/semver"
    license = "MIT"
    generators = "cmake", "cmake_find_package_multi"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

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
        self._cmake.definitions["SEMVER_OPT_BUILD_EXAMPLES"] = False
        self._cmake.definitions["SEMVER_OPT_BUILD_TESTS"] = False
        self._cmake.definitions["SEMVER_OPT_INSTALL"] = True
        self._cmake.configure(source_folder=self._source_subfolder, build_folder=self._build_subfolder)
        return self._cmake

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
        # Exclude compilers not supported
        if compiler not in minimal_version:
            self.output.info("%s requires a compiler that supports at least C++%s" % (self.name, min_req_cppstd))
            return
        if compiler_version < minimal_version[compiler]:
            raise ConanInvalidConfiguration(
                "%s requires a compiler that supports at least C++%s. %s %s is not supported." %
                (self.name, min_req_cppstd, compiler, tools.Version(self.settings.compiler.version.value)))

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], destination=self._source_subfolder, strip_root=True)

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")
        self.copy("*.hpp", dst="include", src=os.path.join(self._source_subfolder, "include"))

    def package_info(self):
        self.cpp_info.names["pkg_config"] = "semver"
        self.cpp_info.names["cmake_find_package"] = "semver"
        self.cpp_info.names["cmake_find_package_multi"] = "semver"

    def package_id(self):
        self.info.header_only()
