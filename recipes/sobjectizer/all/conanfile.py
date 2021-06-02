from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os

class SobjectizerConan(ConanFile):
    name = "sobjectizer"
    license = "BSD-3-Clause"
    homepage = "https://github.com/Stiffstream/sobjectizer"
    url = "https://github.com/conan-io/conan-center-index"
    description = (
            "A framework for simplification of development of sophisticated "
            "concurrent and event-driven applications in C++ "
            "by using Actor, Publish-Subscribe and CSP models."
    )
    topics = ("concurrency", "actor-framework", "actors", "agents", "actor-model", "publish-subscribe", "CSP")
    generators = "cmake"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    exports_sources = ["CMakeLists.txt"]

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        minimal_cpp_standard = "17"
        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, minimal_cpp_standard)
        minimal_version = {
            "gcc": "7",
            "clang": "6",
            "apple-clang": "10",
            "Visual Studio": "15"
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
            raise ConanInvalidConfiguration("%s requires a compiler that supports at least C++%s" % (self.name, minimal_cpp_standard))
        if self.options.shared:
            del self.options.fPIC

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake

        self._cmake = CMake(self)
        self._cmake.definitions["SOBJECTIZER_BUILD_SHARED"] = self.options.shared
        self._cmake.definitions["SOBJECTIZER_BUILD_STATIC"] = not self.options.shared
        self._cmake.definitions["SOBJECTIZER_INSTALL"] = True

        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-v." + self.version
        os.rename(extracted_dir, self._source_subfolder )

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        self.copy("license*", src=self._source_subfolder, dst="licenses",  ignore_case=True, keep_path=False)
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "sobjectizer"
        self.cpp_info.names["cmake_find_package_multi"] = "sobjectizer"
        cmake_target = "SharedLib" if self.options.shared else "StaticLib"
        self.cpp_info.components["_sobjectizer"].names["cmake_find_package"] = cmake_target
        self.cpp_info.components["_sobjectizer"].names["cmake_find_package_multi"] = cmake_target
        self.cpp_info.components["_sobjectizer"].libs = tools.collect_libs(self)
        if self.settings.os == "Linux":
            self.cpp_info.components["_sobjectizer"].system_libs.append("pthread")
        if not self.options.shared:
            self.cpp_info.components["_sobjectizer"].defines.append("SO_5_STATIC_LIB")

