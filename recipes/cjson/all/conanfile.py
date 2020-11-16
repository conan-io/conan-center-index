import os

from conans import ConanFile, CMake, tools

class CjsonConan(ConanFile):
    name = "cjson"
    description = "Ultralightweight JSON parser in ANSI C."
    license = "MIT"
    topics = ("conan", "cjson", "json", "parser")
    homepage = "https://github.com/DaveGamble/cJSON"
    url = "https://github.com/conan-io/conan-center-index"
    exports_sources = ["CMakeLists.txt", "patches/**"]
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "utils": [True, False],
        "use_locales": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "utils": False,
        "use_locales": True
    }

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
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("cJSON-" + self.version, self._source_subfolder)

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["ENABLE_SANITIZERS"] = False
        self._cmake.definitions["ENABLE_SAFE_STACK"] = False
        self._cmake.definitions["ENABLE_PUBLIC_SYMBOLS"] = True
        self._cmake.definitions["ENABLE_HIDDEN_SYMBOLS"] = False
        self._cmake.definitions["ENABLE_TARGET_EXPORT"] = False
        self._cmake.definitions["BUILD_SHARED_AND_STATIC_LIBS"] = False
        self._cmake.definitions["CJSON_OVERRIDE_BUILD_SHARED_LIBS"] = False
        self._cmake.definitions["ENABLE_CJSON_UTILS"] = self.options.utils
        self._cmake.definitions["ENABLE_CJSON_TEST"] = False
        self._cmake.definitions["ENABLE_LOCALES"] = self.options.use_locales
        self._cmake.definitions["ENABLE_FUZZING"] = False
        self._cmake.definitions["ENABLE_CUSTOM_COMPILER_FLAGS"] = False

        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        # FIXME: CMake imported targets shouldn't be namespaced (requires https://github.com/conan-io/conan/issues/7615)
        self.cpp_info.names["cmake_find_package"] = "cJSON"
        self.cpp_info.names["cmake_find_package_multi"] = "cJSON"

        self.cpp_info.components["_cjson"].names["cmake_find_package"] = "cjson"
        self.cpp_info.components["_cjson"].names["cmake_find_package_multi"] = "cjson"
        self.cpp_info.components["_cjson"].names["pkg_config"] = "libcjson"
        self.cpp_info.components["_cjson"].libs = ["cjson"]
        if self.settings.os == "Linux":
            self.cpp_info.components["_cjson"].system_libs = ["m"]

        if self.options.utils:
            self.cpp_info.components["cjson_utils"].names["cmake_find_package"] = "cjson_utils"
            self.cpp_info.components["cjson_utils"].names["cmake_find_package_multi"] = "cjson_utils"
            self.cpp_info.components["cjson_utils"].names["pkg_config"] = "libcjson_utils"
            self.cpp_info.components["cjson_utils"].libs = ["cjson_utils"]
            self.cpp_info.components["cjson_utils"].requires = ["_cjson"]
