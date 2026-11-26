from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import get, copy
from conan.tools.build import check_min_cppstd
from conan.tools.layout import basic_layout
import os

required_conan_version = ">=1.50.0"

class IrcConan(ConanFile):
    name = "irc"
    description = "C++20 Integer Range Containers library"
    license = "MIT"
    homepage = "https://github.com/ichesnokov-irc/irc"
    url = "https://github.com/ichesnokov-irc/irc"
    topics = ("irc", "containers", "C++20", "header-only", "bitset", "set", "unordered_set", "constexpr")
    package_type = "header-library"
    settings = "os", "compiler", "build_type", "arch"
    no_copy_source = True

    @property
    def _min_cppstd(self):
        return "20"


    @property
    def _compilers_minimum_version(self):
        # Minimum compiler versions supporting stable C++20 feature set
        return {
            "gcc": "10",
            "clang": "11",
            "AppleClang": "13",
            "msvc": "192",
        }

    def layout(self):
        # Keeps the sources in the root directory after extracting the archive
        self.folders.source = "."


    def validate(self):
        # 1. Get the current standard, or fallback to the compiler's default if not specified
        cppstd = self.settings.compiler.get_safe("cppstd")
        
        # 2. If a standard is set, ensure it is at least C++20
        if cppstd:
            check_min_cppstd(self, self._min_cppstd)
        else:
            # If no standard is specified in the profile, warn the user or assume compiler default.
            # ConanCenter recipes strictly check the active setting:
            raise ConanInvalidConfiguration(
                f"{self.name} requires C++20. Please specify -s compiler.cppstd=20 in your command or profile."
            )
        
        # 3. Check minimum compiler versions
        compiler = str(self.settings.compiler)
        version = str(self.settings.compiler.version)
        minimum_version = self._compilers_minimum_version.get(compiler)
        if minimum_version and version < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.name} requires C++20 features. Your compiler ({compiler} {version}) is too old."
            )

    def source(self):
        # Downloads your source archive from GitHub based on the version
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        # Copy everything from your repository's 'include' folder to the package 'include' folder
        copy(self, "*", 
             src=os.path.join(self.source_folder, "include"), 
             dst=os.path.join(self.package_folder, "include"))
        
        # ConanCenter strictly requires copying the license file
        copy(self, "LICENSE*", 
             src=self.source_folder, 
             dst=os.path.join(self.package_folder, "licenses"))

    def package_info(self):
        # Inform Conan that there are no compiled libraries or binaries
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
        # Defines the modern CMake target name for users: irc::irc
        self.cpp_info.set_property("cmake_target_name", "irc::irc")
