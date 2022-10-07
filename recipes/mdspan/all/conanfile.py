from conan import ConanFile, tools
from conan.tools import files
from conan.errors import ConanInvalidConfiguration
from conan.tools.microsoft import is_msvc, check_min_vs
from conan.tools.scm import Version
import os

required_conan_version = ">=1.49.0"


class MDSpanConan(ConanFile):
    name = "mdspan"
    homepage = "https://github.com/kokkos/mdspan"
    description = "Production-quality reference implementation of mdspan"
    topics = ("multi-dimensional", "array", "span")
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "compiler"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _minimum_cpp_standard(self):
        return 14

    @property
    def _minimum_compilers_version(self):
        return {
            "msvc": "1911",
            "gcc": "5",
            "clang": "3.4",
            "apple-clang": "5.1"
        }


    # According to upstream issue https://github.com/kokkos/mdspan/issues/26 , the MSVC updates to STL has broke the build
    # since MSVC 16.6; and seems it built successfully on MSVC 17
    def _msvc_is_supported_version(self, version):
        return version < "16.6" or version >= "17.0"


    def configure(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, self._minimum_cpp_standard)
        min_version = self._minimum_compilers_version.get(
            str(self.settings.compiler))
        if not min_version:
            self.output.warn("{} recipe lacks information about the {} "
                             "compiler support.".format(
                                 self.name, self.settings.compiler))
        else:
            compiler_version = Version(self.settings.compiler.version)
            compiler_is_msvc = is_msvc(self)

            if compiler_version < min_version:
                raise ConanInvalidConfiguration(
                    "{} requires C++{} support. "
                    "The current compiler {} {} does not support it.".format(
                        self.name, self._minimum_cpp_standard,
                        self.settings.compiler,
                        compiler_version))
            if compiler_is_msvc and not check_min_vs(self, self._minimum_compilers_version["msvc"]):
                raise ConanInvalidConfiguration(
                    "Unsupported MSVC version {} due to upstream bug. The supported MSVC versions are > 15.0 and < 16.6 or >= 17.0."
                    "See upstream issue https://github.com/kokkos/mdspan/issues/26 for details.".format(
                        compiler_version))
            if compiler_is_msvc and Version(self.version) < "0.4.0" and check_min_vs(conanfile, "1930"): # msc_ver for vs 17.0
                raise ConanInvalidConfiguration(
                    "Old mdspan versions ( < 0.4.0) doesn't build properly on MSVC version {} due to conflicting upstream and STL type_traits (and another issues)."
                    "See upstream issue https://github.com/kokkos/mdspan/issues/22 for details.".format(compiler_version))


    def source(self):
        files.get(self, **self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)

    def package(self):
        self.copy(pattern="*", dst="include", src=os.path.join(self._source_subfolder, "include"))
        self.copy("*LICENSE", dst="licenses", keep_path=False)

    def package_id(self):
        self.info.header_only()

    def package_info(self):
        self.cpp_info.filenames["cmake_find_package"] = "mdspan"
        self.cpp_info.filenames["cmake_find_package_multi"] = "mdspan"
        self.cpp_info.names["cmake_find_package"] = "std"
        self.cpp_info.names["cmake_find_package_multi"] = "std"
        self.cpp_info.components["_mdspan"].names["cmake_find_package"] = "mdspan"
        self.cpp_info.components["_mdspan"].names["cmake_find_package_multi"] = "mdspan"
