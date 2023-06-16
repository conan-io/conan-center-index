from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.files import get, copy
from conan.tools.layout import basic_layout
from conan.tools.scm import Version
import os

required_conan_version = ">=2.0.0"

class PlatformDelegatesConan(ConanFile):
    name = "platform.delegates"
    license = "MIT"
    homepage = "https://github.com/linksplatform/Delegates"
    url = "https://github.com/conan-io/conan-center-index"
    description = """platform.delegates is one of the libraries of the LinksPlatform modular framework, which uses 
    innovations from the C++17 standard, for easier use delegates/events in csharp style."""
    topics = ("linksplatform", "cpp17", "delegates", "events", "header-only")
    settings = "compiler"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _internal_cpp_subfolder(self):
        return os.path.join(self.source_folder, "cpp", "Platform.Delegates")

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "8",
            "Visual Studio": "16",
            "msvc": "19.16",
            "clang": "7",
            "apple-clang": "11"
        }

    @property
    def _min_cppstd(self):
        return "17"

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)

        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(f"{self.ref} requires C++{self._min_cppstd}, "
                                            "which is not supported "
                                            f"by {self.settings.compiler} {self.settings.compiler.version}.")

    def source(self):
        get(self, **self.conan_data["sources"][self.version]["source"], strip_root=True)

    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        copy(self, pattern="*.h", dst=os.path.join(self.package_folder, "include"), src=self._internal_cpp_subfolder)

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.set_property("cmake_file_name", "Platform.Delegates")
        self.cpp_info.set_property("cmake_target_name", "Platform.Delegates::Platform.Delegates")
        self.cpp_info.names["cmake_find_package"] = "Platform.Delegates"
        self.cpp_info.names["cmake_find_package_multi"] = "Platform.Delegates"

