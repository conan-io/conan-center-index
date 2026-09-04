import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get, save
from conan.tools.layout import basic_layout
from conan.tools.scm import Version

required_conan_version = ">=2.0"


class LibfnConan(ConanFile):
    name = "libfn"
    description = "Functional programming in C++"
    license = "ISC"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://libfn.org"
    topics = ("functional-programming", "monadic", "expected", "optional", "header-only")
    package_type = "header-library"
    # Settings are needed to read the consumer's compiler in package_info();
    # package_id() clears them, so the package stays identical for everyone.
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    @property
    def _min_cppstd(self):
        return 20

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "12",
            "clang": "16",
            "apple-clang": "16",
            "msvc": "193",
        }

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        # Intentional: header-only library, so the package is identical for every consumer.
        self.info.clear()

    def validate(self):
        check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler))
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++20, which {self.settings.compiler} {self.settings.compiler.version} does not fully support."
            )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def build(self):
        pass

    def package(self):
        copy(
            self,
            pattern="*.hpp",
            src=os.path.join(self.source_folder, "include"),
            dst=os.path.join(self.package_folder, "include"),
        )
        copy(
            self,
            pattern="LICENSE.md",
            src=self.source_folder,
            dst=os.path.join(self.package_folder, "licenses"),
        )
        # CMakeDeps synthesizes its own targets and drops the compile features the CMake
        # export carries; this build module restores fn_cxx26's language requirement.
        save(
            self,
            os.path.join(self.package_folder, "cmake", "libfn-cxx26.cmake"),
            "if(TARGET libfn::fn_cxx26)\n"
            "  target_compile_features(libfn::fn_cxx26 INTERFACE cxx_std_26)\n"
            "endif()\n",
        )

    def package_info(self):
        # find_package(libfn) -> libfn::libfn aggregate target,
        # plus libfn::fn, libfn::fn_cxx26 and libfn::pfn component targets.
        self.cpp_info.set_property("cmake_file_name", "libfn")
        self.cpp_info.set_property("cmake_target_name", "libfn::libfn")
        self.cpp_info.set_property("cmake_build_modules", [os.path.join("cmake", "libfn-cxx26.cmake")])

        # fn: the main component (headers under include/fn/); built on the pfn polyfills.
        fn = self.cpp_info.components["fn"]
        fn.set_property("cmake_target_name", "libfn::fn")
        fn.bindirs = []
        fn.libdirs = []
        fn.includedirs = ["include"]
        fn.requires = ["pfn"]

        # pfn: the C++20 component (headers under include/pfn/).
        pfn = self.cpp_info.components["pfn"]
        pfn.set_property("cmake_target_name", "libfn::pfn")
        pfn.bindirs = []
        pfn.libdirs = []
        pfn.includedirs = ["include"]

        # fn_cxx26: fn with the C++26 mode selected; owns no headers.
        # A consumer links exactly one of libfn::fn / libfn::fn_cxx26.
        fn_cxx26 = self.cpp_info.components["fn_cxx26"]
        fn_cxx26.set_property("cmake_target_name", "libfn::fn_cxx26")
        fn_cxx26.bindirs = []
        fn_cxx26.libdirs = []
        fn_cxx26.includedirs = []
        fn_cxx26.requires = ["fn"]
        fn_cxx26.defines = ["LIBFN_CXX26"]

        # CMakeDeps synthesizes its own targets, so the INTERFACE compile options
        # exported by the CMake package do not reach conan consumers; mirror
        # upstream cmake/CompilationOptions.cmake (append_compilation_options INTERFACE) here.
        compiler = self.settings.get_safe("compiler")
        for component in (fn, pfn):
            if compiler == "msvc":
                component.cxxflags.append("/permissive-")
                component.defines.append("_HAS_CXX23")
            elif compiler in ("clang", "apple-clang"):
                component.cxxflags.append("-Wno-missing-braces")
