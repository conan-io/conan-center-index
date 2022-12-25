from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import collect_libs, copy, get, load, replace_in_file, rmdir, save
from conan.tools.layout import basic_layout
import os

required_conan_version = ">=1.50.0"


class PugiXmlConan(ConanFile):
    name = "pugixml"
    description = "Light-weight, simple and fast XML parser for C++ with XPath support"
    topics = ("xml-parser", "xpath", "xml", "dom")
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://pugixml.org/"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "header_only": [True, False],
        "wchar_mode": [True, False],
        "no_exceptions": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "header_only": False,
        "wchar_mode": False,
        "no_exceptions": False,
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        if self.options.header_only:
            if self.settings.os != "Windows":
                del self.options.fPIC
            del self.options.shared

    def layout(self):
        if self.options.header_only:
            basic_layout(self, src_folder="src")
        else:
            cmake_layout(self, src_folder="src")

    def package_id(self):
        if self.options.header_only:
            self.info.clear()

    def validate(self):
        if self.options.get_safe("shared") and self.options.wchar_mode:
            # The app crashes with error "The procedure entry point ... could not be located in the dynamic link library"
            raise ConanInvalidConfiguration("Combination of 'shared' and 'wchar_mode' options is not supported")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        if not self.options.header_only:
            tc = CMakeToolchain(self)
            tc.variables["BUILD_TESTS"] = False
            # For msvc shared
            tc.variables["CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS"] = True
            # Honor BUILD_SHARED_LIBS from conan_toolchain (see https://github.com/conan-io/conan/issues/11840)
            tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0077"] = "NEW"
            tc.generate()

    def build(self):
        if not self.options.header_only:
            header_file = os.path.join(self.source_folder, "src", "pugiconfig.hpp")
            # For the library build mode, options applied via change the configuration file
            if self.options.wchar_mode:
                replace_in_file(self, header_file, "// #define PUGIXML_WCHAR_MODE", "#define PUGIXML_WCHAR_MODE")
            if self.options.no_exceptions:
                replace_in_file(self, header_file, "// #define PUGIXML_NO_EXCEPTIONS", "#define PUGIXML_NO_EXCEPTIONS")
            cmake = CMake(self)
            cmake.configure()
            cmake.build()

    def package(self):
        readme_contents = load(self, os.path.join(self.source_folder, "readme.txt"))
        license_contents = readme_contents[readme_contents.find("This library is"):]
        save(self, os.path.join(self.package_folder, "licenses", "LICENSE"), license_contents)
        if self.options.header_only:
            source_dir = os.path.join(self.source_folder, "src")
            copy(self, "*", src=source_dir, dst=os.path.join(self.package_folder, "include"))
        else:
            cmake = CMake(self)
            cmake.install()
            rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
            rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "pugixml")
        self.cpp_info.set_property("cmake_target_name", "pugixml::pugixml")
        self.cpp_info.set_property("pkg_config_name", "pugixml")
        self.cpp_info.resdirs = []
        if self.options.header_only:
            # For the "header_only" mode, options applied via global definitions
            self.cpp_info.defines.append("PUGIXML_HEADER_ONLY")
            if self.options.wchar_mode:
                self.cpp_info.defines.append("PUGIXML_WCHAR_MODE")
            if self.options.no_exceptions:
                self.cpp_info.defines.append("PUGIXML_NO_EXCEPTIONS")
            self.cpp_info.bindirs = []
            self.cpp_info.libdirs = []
        else:
            self.cpp_info.set_property(
                "cmake_target_aliases",
                ["pugixml::shared"] if self.options.shared else ["pugixml::static"],
            )
            self.cpp_info.libs = collect_libs(self)
