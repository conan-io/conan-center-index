from conans import ConanFile, tools
from conan.errors import ConanInvalidConfiguration

import os

required_conan_version = ">=1.33.0"


class TCSBankUconfigConan(ConanFile):
    name = "tcsbank-uconfig"
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

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def requirements(self):
        if self.options.with_rapidjson:
            self.requires("rapidjson/1.1.0")

    def validate(self):
        compiler = str(self.settings.compiler)
        compiler_version = tools.scm.Version(self.settings.compiler.version)

        min_req_cppstd = "17"
        if self.settings.compiler.cppstd:
            tools.build.check_min_cppstd(self, min_req_cppstd)
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
        tools.files.get(self, **self.conan_data["sources"][self.version], destination=self._source_subfolder, strip_root=True)

    def package(self):
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")
        self.copy("*.h", dst="include", src=os.path.join(self._source_subfolder, "include"))
        self.copy("*.ipp", dst="include", src=os.path.join(self._source_subfolder, "include"))

    def package_info(self):
        self.cpp_info.names["pkg_config"] = "uconfig"
        self.cpp_info.names["cmake_find_package"] = "uconfig"
        self.cpp_info.names["cmake_find_package_multi"] = "uconfig"
        if self.options.with_rapidjson:
            self.cpp_info.defines = ["RAPIDJSON_HAS_STDSTRING=1"]

    def package_id(self):
        self.info.header_only()
