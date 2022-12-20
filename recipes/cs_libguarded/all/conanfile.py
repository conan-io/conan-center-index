from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.files import get, copy
from conan.tools.layout import basic_layout
from conan.tools.scm import Version
import os

required_conan_version = ">=1.52.0"

class CsLibguardedConan(ConanFile):
    name = "cs_libguarded"
    description = "The libGuarded library is a standalone header-only library for multithreaded programming."
    license = "BSD-2-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/copperspice/libguarded"
    topics = ("multithreading", "templates", "cpp14", "mutexes", "header-only")
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    @property
    def _min_cppstd(self):
        return 14 if Version(self.version) < "1.3" else 17

    @property
    def _compilers_minimum_version(self):
        if Version(self.version) < "1.3":
            return {
                "Visual Studio": "15.2",
                "msvc": "191",
                "gcc": "5",
                "clang": "5",
                "apple-clang": "5",
            }
        else:
            return {
                "Visual Studio": "16",
                "msvc": "192",
                "gcc": "8",
                "clang": "7",
                "apple-clang": "12",
            }

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)

        def loose_lt_semver(v1, v2):
            lv1 = [int(v) for v in v1.split(".")]
            lv2 = [int(v) for v in v2.split(".")]
            min_length = min(len(lv1), len(lv2))
            return lv1[:min_length] < lv2[:min_length]

        compiler = str(self.settings.compiler)
        version = str(self.settings.compiler.version)

        minimum_version = self._compilers_minimum_version.get(compiler, False)
        if minimum_version and loose_lt_semver(version, minimum_version):
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler ({compiler}-{version}) does not support")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], destination=self.source_folder, strip_root=True)

    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        if Version(self.version) < "1.3":
            copy(
                self,
                pattern="*.hpp",
                dst=os.path.join(self.package_folder, "include"),
                src=os.path.join(self.source_folder, "src"),
            )
        else:
            copy(
                self,
                pattern="*.h",
                dst=os.path.join(self.package_folder, "include", "CsLibGuarded"),
                src=os.path.join(self.source_folder, "src"),
            )

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []

        if Version(self.version) >= "1.3":
            self.cpp_info.includedirs.append(os.path.join("include", "CsLibGuarded"))

            self.cpp_info.set_property("cmake_file_name", "CsLibGuarded")
            self.cpp_info.set_property("cmake_target_name", "CsLibGuarded::CsLibGuarded")

            # TODO: to remove in conan v2 once cmake_find_package_* generators removed
            self.cpp_info.filenames["cmake_find_package"] = "CsLibGuarded"
            self.cpp_info.filenames["cmake_find_package_multi"] = "CsLibGuarded"
            self.cpp_info.names["cmake_find_package"] = "CsLibGuarded"
            self.cpp_info.names["cmake_find_package_multi"] = "CsLibGuarded"
