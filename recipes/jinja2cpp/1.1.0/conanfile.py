import os
import re
from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration


class Jinja2cppConan(ConanFile):
    name = "jinja2cpp"
    license = "MIT"
    homepage = "https://jinja2cpp.dev/"
    url = "https://github.com/conan-io/conan-center-index"
    description = "Jinja2 C++ (and for C++) almost full-conformance template engine implementation"
    topics = ("conan", "cpp14", "cpp17", "jinja2", "string templates", "templates engine")
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake", "cmake_find_package"
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False], "fPIC": [True, False]
    }
    default_options = {'shared': False, "fPIC": True}
    requires = (
        "variant-lite/1.2.2",
        "expected-lite/0.3.0",
        "optional-lite/3.2.0",
        "string-view-lite/1.3.0",
        "boost/1.72.0",
        "fmt/6.1.2",
        "rapidjson/1.1.0"
    )
    
    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"
    _cpp_std = 14

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

        cppstd = self.settings.get_safe("compiler.cppstd")
        if cppstd:
            cppstd_pattern = re.compile(r'^(gnu)?(?P<cppstd>\d+)$')
            m = cppstd_pattern.match(cppstd)
            cppstd_profile = int(m.group("cppstd"))
            if cppstd_profile < 14:
                raise ConanInvalidConfiguration("Minimum C++ Standard required is 14 (provided '{}')".format(cppstd))
            else:
                self._cpp_std = cppstd_profile

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = "Jinja2Cpp-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def build(self):
        cmake = CMake(self)
        cmake.definitions["JINJA2CPP_BUILD_TESTS"] = False
        cmake.definitions["JINJA2CPP_STRICT_WARNINGS"] = False
        cmake.definitions["JINJA2CPP_BUILD_SHARED"] = self.options.shared
        cmake.definitions["JINJA2CPP_DEPS_MODE"] = "conan-build"
        cmake.definitions["JINJA2CPP_CXX_STANDARD"] = self._cpp_std
        # Conan cmake generator omits the build_type flag for MSVC multiconfiguration CMake,
        # but provide build-type-specific runtime type flag. For now, Jinja2C++ build scripts
        # need to know the build type is being built in order to setup internal flags correctly
        cmake.definitions["JINJA2CPP_CONAN_BUILD_TYPE"] = self.settings.build_type
        compiler = self.settings.get_safe("compiler")
        if compiler == 'Visual Studio':
            # Runtime type configuration for Jinja2C++ should be strictly '/MT' or '/MD'
            runtime = self.settings.get_safe("compiler.runtime")            
            if runtime == 'MTd':
                runtime = 'MT'
            if runtime == 'MDd':
                runtime = 'MD'
            cmake.definitions["JINJA2CPP_MSVC_RUNTIME_TYPE"] = '/' + runtime
            
        cmake.configure(build_folder=self._build_subfolder)
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy("*.h", dst="include", src=os.path.join(self._source_subfolder, "include"))
        self.copy("*.hpp", dst="include", src=os.path.join(self._source_subfolder, "include"))
        self.copy("*.lib", dst="lib", keep_path=False)
        self.copy("*.dll", dst="bin", keep_path=False)
        self.copy("*.so", dst="lib", keep_path=False)
        self.copy("*.so.*", dst="lib", keep_path=False)
        self.copy("*.dylib", dst="lib", keep_path=False)
        self.copy("*.a", dst="lib", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = ["jinja2cpp"]

