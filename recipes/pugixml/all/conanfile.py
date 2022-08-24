from conan import ConanFile, tools
from conans import CMake
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.33.0"

class PugiXmlConan(ConanFile):
    name = "pugixml"
    description = "Light-weight, simple and fast XML parser for C++ with XPath support"
    topics = ("xml-parser", "xpath", "xml", "dom")
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://pugixml.org/"
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake"
    settings = ("os", "arch", "compiler", "build_type")
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "header_only": [True, False],
        "wchar_mode": [True, False],
        "no_exceptions": [True, False]
    }
    default_options = {
        'shared': False,
        'fPIC': True,
        'header_only': False,
        'wchar_mode': False,
        'no_exceptions': False
    }

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        if self.options.header_only:
            if self.settings.os != 'Windows':
                del self.options.fPIC
            del self.options.shared

    def validate(self):
        if self.options.get_safe("shared") and self.options.wchar_mode:
            # The app crashes with error "The procedure entry point ... could not be located in the dynamic link library"
            raise ConanInvalidConfiguration("Combination of 'shared' and 'wchar_mode' options is not supported")

    def package_id(self):
        if self.options.header_only:
            self.info.header_only()

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
            destination=self._source_subfolder, strip_root=True)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["BUILD_TESTS"] = False
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        if not self.options.header_only:
            header_file = os.path.join(self._source_subfolder, "src", "pugiconfig.hpp")
            # For the library build mode, options applied via change the configuration file
            if self.options.wchar_mode:
                tools.replace_in_file(header_file, "// #define PUGIXML_WCHAR_MODE", '''#define PUGIXML_WCHAR_MODE''')
            if self.options.no_exceptions:
                tools.replace_in_file(header_file, "// #define PUGIXML_NO_EXCEPTIONS", '''#define PUGIXML_NO_EXCEPTIONS''')
            cmake = self._configure_cmake()
            cmake.build()

    def package(self):
        readme_contents = tools.load(os.path.join(self._source_subfolder, "readme.txt"))
        license_contents = readme_contents[readme_contents.find("This library is"):]
        tools.save(os.path.join(self.package_folder, "licenses", "LICENSE"), license_contents)
        if self.options.header_only:
            source_dir = os.path.join(self._source_subfolder, "src")
            self.copy(pattern="*", dst="include", src=source_dir)
        else:
            cmake = self._configure_cmake()
            cmake.install()
            tools.files.rmdir(self, os.path.join(self.package_folder, 'lib', 'cmake'))
            tools.files.rmdir(self, os.path.join(self.package_folder, 'lib', 'pkgconfig'))

    def package_info(self):
        if self.options.header_only:
            # For the "header_only" mode, options applied via global definitions
            self.cpp_info.defines.append("PUGIXML_HEADER_ONLY")
            if self.options.wchar_mode:
                self.cpp_info.defines.append("PUGIXML_WCHAR_MODE")
            if self.options.no_exceptions:
                self.cpp_info.defines.append("PUGIXML_NO_EXCEPTIONS")
        else:
            self.cpp_info.libs = tools.collect_libs(self)
