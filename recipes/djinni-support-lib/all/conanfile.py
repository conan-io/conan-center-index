import os

from conans import ConanFile, CMake, tools

class DjinniSuppotLib(ConanFile):
    name = "djinni-support-lib"
    homepage = "https://djinni.xlcpp.dev"
    url = "https://github.com/conan-io/conan-center-index"
    description = "Djinni is a tool for generating cross-language type declarations and interface bindings"
    topics = ("java", "Objective-C", "Android", "iOS")
    license = "Apache-2.0"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False],
                "fPIC": [True, False],
                "target": ["jni", "objc", "auto"],
                "system_java": [True, False]
               }
    default_options = {"shared": False,
                        "fPIC": True ,
                        "target": "auto",
                        "system_java": False
                       }
    exports_sources = ["patches/**", "CMakeLists.txt"]
    generators = "cmake", "cmake_find_package"

    _cmake = None

    @property
    def objc_support(self):
        if self.options.target == "auto":
            return tools.is_apple_os(self.settings.os)
        else:
            return self.options.target == "objc"

    @property
    def jni_support(self):
        if self.options.target == "auto":
            return self.settings.os not in ["iOS", "watchOS", "tvOS"]
        else:
            return self.options.target == "jni"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def build_requirements(self):
        if not self.options.system_java:
            self.build_requires("zulu-openjdk/11.0.8@")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  strip_root=True, destination=self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        if not self.options.shared:
            self._cmake.definitions["DJINNI_STATIC_LIB"] = True
        self._cmake.definitions["DJINNI_WITH_OBJC"] = self.objc_support
        self._cmake.definitions["DJINNI_WITH_JNI"] = self.jni_support
        if self.jni_support:
            self._cmake.definitions["JAVA_AWT_LIBRARY"] = "NotNeeded"
            self._cmake.definitions["JAVA_AWT_INCLUDE_PATH"] = "NotNeeded"
        self._cmake.configure()
        return self._cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        # these should not be here, but to support old generated files ....
        if self.objc_support:
            self.cpp_info.includedirs.append(os.path.join("include", "djinni", "objc"))
        if self.jni_support:
            self.cpp_info.includedirs.append(os.path.join("include", "djinni", "jni"))
