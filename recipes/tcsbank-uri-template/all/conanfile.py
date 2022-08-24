from conan import ConanFile, tools
from conans import CMake
from conan.errors import ConanInvalidConfiguration

import os

required_conan_version = ">=1.33.0"


class TCSBankUriTemplateConan(ConanFile):
    name = "tcsbank-uri-template"
    description = "URI Templates expansion and reverse-matching for C++"
    topics = ("conan", "uri-template", "url-template", "rfc-6570")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/TinkoffCreditSystems/uri-template"
    license = "Apache-2.0"

    generators = "cmake", "cmake_find_package_multi"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }
    exports_sources = [
        "CMakeLists.txt",
        "patches/*",
    ]

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
        self._cmake.definitions["URITEMPLATE_BUILD_TESTING"] = False
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def validate(self):
        compiler_name = str(self.settings.compiler)
        compiler_version = tools.scm.Version(self.settings.compiler.version)

        # Exclude compiler.cppstd < 17
        min_req_cppstd = "17"
        if self.settings.compiler.cppstd:
            tools.build.check_min_cppstd(self, min_req_cppstd)
        else:
            self.output.warn("%s recipe lacks information about the %s compiler"
                             " standard version support." % (self.name, compiler_name))

        # Exclude not supported compilers
        compilers_required = {
            "Visual Studio": "16",
            "gcc": "7.3",
            "clang": "6.0",
            "apple-clang": "10.0",
        }
        if compiler_name not in compilers_required or compiler_version < compilers_required[compiler_name]:
            raise ConanInvalidConfiguration(
                "%s requires a compiler that supports at least C++%s. %s %s is not supported." %
                (self.name, min_req_cppstd, compiler_name, compiler_version))

        # Check stdlib ABI compatibility
        if compiler_name == "gcc" and self.settings.compiler.libcxx != "libstdc++11":
            raise ConanInvalidConfiguration('Using %s with GCC requires "compiler.libcxx=libstdc++11"' % self.name)
        elif compiler_name == "clang" and self.settings.compiler.libcxx not in ["libstdc++11", "libc++"]:
            raise ConanInvalidConfiguration('Using %s with Clang requires either "compiler.libcxx=libstdc++11"'
                                            ' or "compiler.libcxx=libc++"' % self.name)

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version], destination=self._source_subfolder, strip_root=True)

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.names["pkg_config"] = "uri-template"
        self.cpp_info.names["cmake_find_package"] = "uri-template"
        self.cpp_info.names["cmake_find_package_multi"] = "uri-template"
        self.cpp_info.libs = tools.files.collect_libs(self, self)
