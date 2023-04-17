from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version
import os

required_conan_version = ">=1.50.0"


class SigslotConan(ConanFile):
    name = "sigslot"
    description = "Sigslot is a header-only, thread safe implementation of signal-slots for C++."
    topics = ("signal", "slot", "c++14", "header-only")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/palacaze/sigslot"
    license = "MIT"
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    @property
    def _min_cppstd(self):
        return "14"

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "5",
            "clang": "3.4",
            "apple-clang": "10",
            "Visual Studio": "15",  # 14 is not supported by the library
            "msvc": "191",
        }

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)

        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def build(self):
        pass

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "signal.hpp", src=os.path.join(self.source_folder, "include", "sigslot"),
                                 dst=os.path.join(self.package_folder, "include", "sigslot"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "PalSigslot")
        self.cpp_info.set_property("cmake_target_name", "Pal::Sigslot")
        # TODO: back to global scope in conan v2 once cmake_find_package* generators removed
        self.cpp_info.components["_sigslot"].bindirs = []
        self.cpp_info.components["_sigslot"].libdirs = []
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["_sigslot"].system_libs.append("pthread")
        elif self.settings.os == "Windows":
            if is_msvc(self) or self.settings.compiler == "clang":
                self.cpp_info.components["_sigslot"].exelinkflags.append('-OPT:NOICF')

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "PalSigslot"
        self.cpp_info.filenames["cmake_find_package_multi"] = "PalSigslot"
        self.cpp_info.names["cmake_find_package"] = "Pal"
        self.cpp_info.names["cmake_find_package_multi"] = "Pal"
        self.cpp_info.components["_sigslot"].names["cmake_find_package"] = "Sigslot"
        self.cpp_info.components["_sigslot"].names["cmake_find_package_multi"] = "Sigslot"
        self.cpp_info.components["_sigslot"].set_property("cmake_target_name", "Pal::Sigslot")
