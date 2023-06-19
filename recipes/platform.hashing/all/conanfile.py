from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.files import get, copy
from conan.tools.scm import Version
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=2.0.0"


class PlatformInterfacesConan(ConanFile):
    name = "platform.hashing"
    license = "LGPL-3.0-only"
    homepage = "https://github.com/linksplatform/Hashing"
    url = "https://github.com/conan-io/conan-center-index"
    description = "platform.hashing is one of the libraries of the LinksPlatform modular framework, " \
                  "which contains std::hash specializations for:\n" \
                  " - trivial and standard-layout types\n" \
                  " - types constrained by std::ranges::range\n" \
                  " - std::any"
    topics = ("linksplatform", "cpp20", "hashing", "any", "ranges", "native")
    settings = "compiler", "arch"
    no_copy_source = True

    @property
    def _subfolder_sources(self):
        return os.path.join(self.source_folder, "cpp", "Platform.Hashing")

    @property
    def _internal_cpp_subfolder(self):
        return os.path.join(self._source_subfolder, "cpp", "Platform.Hashing")

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "10",
            "Visual Studio": "16",
            "clang": "14",
            "apple-clang": "14"
        }

    @property
    def _minimum_cpp_standard(self):
        return 20

    def validate(self):
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler))

        if not minimum_version:
            self.output.warn(f"{self.name} recipe lacks information about the {self.settings.compiler} compiler support.")

        elif Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(f"{self.ref} requires c++{self._minimum_cpp_standard}, "
                                            f"which is not supported by {self.settings.compiler} {self.settings.compiler.version}.")

        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._minimum_cpp_standard)

        if self.settings.arch in ("x86", ):
            raise ConanInvalidConfiguration(f"{self.name} does not support arch={self.settings.arch}")

    def package_id(self):
        self.info.clear()

    def source(self):
        get(self, **self.conan_data["sources"][self.version]["source"], strip_root=True)

    def package(self):
        copy(
                self,
                pattern="*.h",
                dst=os.path.join(self.package_folder, "include"),
                src=self.source_folder,
            )
        copy(self, pattern="LICENSE", dst="licenses", src=self.source_folder)

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []

        suggested_flags = ""
        if self.settings.compiler != "msvc":
            suggested_flags = {
                "x86_64": "-march=haswell",
                "armv7": "-march=armv7",
                "armv8": "-march=armv8-a",
            }.get(str(self.settings.arch), "")
            
        self.cpp_info.set_property("suggested_flags", suggested_flags)

        if "-march" not in "{} {}".format(os.environ.get("CPPFLAGS", ""), os.environ.get("CXXFLAGS", "")):
            self.output.warning(f"platform.hashing needs to have `-march=ARCH` added to CPPFLAGS/CXXFLAGS. "
                            f"A suggestion is available in the property '{self.name}:suggested_flags'.")

        self.cpp_info.set_property("cmake_file_name", "Platform.Hashing")
        self.cpp_info.set_property("cmake_target_name", "Platform.Hashing::Platform.Hashing")

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.names["cmake_find_package"] = "Platform.Hashing"
        self.cpp_info.names["cmake_find_package_multi"] = "Platform.Hashing"

