from conans import ConanFile, CMake, tools
import os


class ChaiScriptConan(ConanFile):
    name = "chaiscript"
    homepage = "https://github.com/ChaiScript/ChaiScript"
    description = "Embedded Scripting Language Designed for C++."
    topics = ("conan", "embedded-scripting-language", "language")
    url = "https://github.com/conan-io/conan-center-index"
    license = "BSD-3-Clause"
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False], "dyn_load": [True, False], "use_std_make_shared": [True, False],
               "multithread_support": [True, False]}
    default_options = {"shared": False, "fPIC": True, "dyn_load": True, "use_std_make_shared": True,
                       "multithread_support": True}

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = "ChaiScript-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["USE_STD_MAKE_SHARED"] = self.options.use_std_make_shared
        cmake.definitions["DYNLOAD_ENABLED"] = self.options.dyn_load
        cmake.definitions["MULTITHREAD_SUPPORT_ENABLED"] = self.options.multithread_support
        cmake.configure(build_folder=self._build_subfolder)
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if self.options.use_std_make_shared:
            self.cpp_info.defines.append("CHAISCRIPT_USE_STD_MAKE_SHARED")
        if self.settings.os == "Linux":
            self.cpp_info.system_libs = ["dl"]
            if self.options.multithread_support:
                self.cpp_info.system_libs.append("pthread")
