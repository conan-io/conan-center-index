import os

from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration

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
                "target": ["jni", "objc", "python", "cppcli", "auto"],
                "system_java": [True, False]
               }
    default_options = {"shared": False,
                        "fPIC": True ,
                        "target": "auto",
                        "system_java": False,
                       }
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake", "cmake_find_package"

    _cmake = None

    @property
    def _objc_support(self):
        if self.options.target == "auto":
            return tools.is_apple_os(self.settings.os)
        else:
            return self.options.target == "objc"

    @property
    def _jni_support(self):
        if self.options.target == "auto":
            return self.settings.os == "Android"
        else:
            return self.options.target == "jni"

    @property
    def _python_support(self):
        return self.options.target == "python"

    @property
    def _cppcli_support(self):
        if self.options.target == "auto":
            return self.settings.os  == "Windows"
        else:
            return self.options.target == "cppcli"

    def configure(self):
        if self.settings.compiler == "Visual Studio" or self.options.shared:
            del self.options.fPIC

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def build_requirements(self):
        if not self.options.system_java and self._jni_support:
            self.build_requires("zulu-openjdk/11.0.8@")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        elif self.settings.os == "Android":
            self.options.system_java = True

    @property
    def _supported_compilers(self):
        return {
            "gcc": "8",
            "clang": "7",
            "Visual Studio": "15",
            "apple-clang": "10",
        }

    def validate(self):
        if not (self._objc_support or self._jni_support or self._python_support or self._cppcli_support):
            raise ConanInvalidConfiguration("Target language could not be determined automatically. Set target explicitly to one of 'jni', 'objc', 'python' or 'cppcli'")
        if self._cppcli_support and (self.settings.compiler.runtime == "MT" or self.settings.compiler.runtime == "MTd"):
            raise ConanInvalidConfiguration("'/clr' and '/MT' command-line options are incompatible")
        if self.options.shared and self._cppcli_support:
            raise ConanInvalidConfiguration("C++/CLI does not support building as shared library")
        if self.settings.get_safe("compiler.cppstd"):
            tools.check_min_cppstd(self, "17")
        try:
            minimum_required_compiler_version = self._supported_compilers[str(self.settings.compiler)]
            if tools.Version(self.settings.compiler.version) < minimum_required_compiler_version:
                raise ConanInvalidConfiguration("This package requires c++17 support. The current compiler does not support it.")
        except KeyError:
            self.output.warn("This recipe has no support for the current compiler. Please consider adding it.")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["DJINNI_WITH_OBJC"] = self._objc_support
        self._cmake.definitions["DJINNI_WITH_JNI"] = self._jni_support
        self._cmake.definitions["DJINNI_WITH_PYTHON"] = self._python_support
        self._cmake.definitions["DJINNI_WITH_CPPCLI"] = self._cppcli_support
        self._cmake.definitions["BUILD_TESTING"] = False
        if self._jni_support:
            self._cmake.definitions["JAVA_AWT_LIBRARY"] = "NotNeeded"
            self._cmake.definitions["JAVA_AWT_INCLUDE_PATH"] = "NotNeeded"
        self._cmake.configure()
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
