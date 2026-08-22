from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.files import get, copy, download
from conan.tools.layout import basic_layout
from conan.tools.scm import Version
import os

required_conan_version = ">=1.52.0"

class PlatformInterfacesConan(ConanFile):
    name = "platform.interfaces"
    description = """platform.interfaces is one of the libraries of the LinksPlatform modular framework, which uses
    innovations from the C++20 standard, for easier use of static polymorphism. It also includes some auxiliary
    structures for more convenient work with containers."""
    license = "Unlicense"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/linksplatform/Interfaces"
    topics = ("platform", "concepts", "header-only")
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    @property
    def _subfolder_sources(self):
        return os.path.join(self.source_folder, "cpp", "Platform.Interfaces")

    @property
    def _min_cppstd(self):
        return "20"

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "11",
            "Visual Studio": "16",
            "msvc": "193",
            "clang": "13",
        }

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.settings.compiler == "apple-clang":
            raise ConanInvalidConfiguration(f"{self.ref} requires C++{self._min_cppstd}, "
                                            "which is not supported "
                                            f"by {self.settings.compiler}.")

        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)

        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(f"{self.ref} requires C++{self._min_cppstd}, "
                                            "which is not supported "
                                            "by {self.settings.compiler} {self.settings.compiler.version}.")

    def source(self):
        get(self, **self.conan_data["sources"][self.version]["source"], strip_root=True)
        if Version(self.version) >= "0.3.41":
            download(self, **self.conan_data["sources"][self.version]["license"], filename="LICENSE")

    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)

        if Version(self.version) < "0.3.41":
            copy(
                self,
                pattern="*.h",
                dst=os.path.join(self.package_folder, "include"),
                src=os.path.join(self.source_folder, "cpp", "Platform.Interfaces"),
            )
        else:
            copy(
                self,
                pattern="*.h",
                dst=os.path.join(self.package_folder, "include"),
                src=self.source_folder,
            )

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []

        self.cpp_info.set_property("cmake_file_name", "Platform.Interfaces")
        self.cpp_info.set_property("cmake_target_name", "Platform.Interfaces::Platform.Interfaces")

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.names["cmake_find_package"] = "Platform.Interfaces"
        self.cpp_info.names["cmake_find_package_multi"] = "Platform.Interfaces"
