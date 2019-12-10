import os
from conans import ConanFile, CMake, tools


class CprConan(ConanFile):
    name = "cpr"

    url = "https://github.com/conan-io/conan-center-index"
    description = "Keep it short"
    license = "https://github.com/whoshuu/cpr/blob/1.3.0/LICENSE"
    homepage = "https://whoshuu.github.io/cpr/"
    exports_sources = ["CMakeLists.txt", "patches/*"]
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False],
               "use_ssl": [True, False],
               "fPIC": [True, False]}
    default_options = {"shared": False,
                       #"libcurl:with_ldap": False,
                       "use_ssl": True,
                       "fPIC": True}

    generators = "cmake"
    _source_subfolder = "cpr"

    def requirements(self):
        self.requires("libcurl/7.66.0")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if self.options.use_ssl:
            self.options["libcurl"].with_openssl = True
        else:
            self.options["libcurl"].with_openssl = False

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)

    def build(self):
        cmake = CMake(self)
        cmake.definitions["USE_SYSTEM_CURL"] = True # Force CPR to not try to build curl itself from a git submodule
        cmake.definitions["BUILD_CPR_TESTS"] = False
        cmake.definitions["GENERATE_COVERAGE"] = False
        cmake.definitions["USE_SYSTEM_GTEST"] = False
        cmake.configure()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE", src=self._source_subfolder, dst="licenses")
        self.copy(pattern="*.h", dst="include", src=os.path.join(self._source_subfolder, 'include'), keep_path=True)
        self.copy(pattern="*.dll", dst="bin", src="bin", keep_path=False)
        self.copy(pattern="*.lib", dst="lib", src="lib", keep_path=False)
        self.copy(pattern="*.a", dst="lib", src="lib", keep_path=False)
        self.copy(pattern="*.so*", dst="lib", src="lib", keep_path=False)
        self.copy(pattern="*.dylib", dst="lib", src="lib", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = ["cpr"]
