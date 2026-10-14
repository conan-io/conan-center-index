import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir
from conan.tools.scm import Version

required_conan_version = ">=2.0.9"


class LibfnConan(ConanFile):
    name = "libfn"
    description = "Functional programming in C++"
    license = "ISC"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://libfn.org"
    topics = ("functional-programming", "monadic", "expected", "optional", "header-only")
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "cxx26": [True, False],
    }
    default_options = {
        "cxx26": False,
    }
    no_copy_source = True

    def layout(self):
        cmake_layout(self, src_folder="src")

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.25]")

    def package_id(self):
        self.info.clear()

    def validate(self):
        check_min_cppstd(self, 26 if self.options.cxx26 else 20)
        compilers_minimum_version = {"gcc": "12", "clang": "16", "apple-clang": "16", "msvc": "193"}
        minimum_version = compilers_minimum_version.get(str(self.settings.compiler))
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++20, which {self.settings.compiler} {self.settings.compiler.version} does not fully support."
            )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["LIBFN_TESTS"] = False
        tc.cache_variables["DISABLE_CCACHE_DETECTION"] = True
        # Upstream would symlink compile_commands.json into the shared source folder
        tc.cache_variables["CMAKE_EXPORT_COMPILE_COMMANDS"] = False
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()

    def package(self):
        copy(
            self,
            pattern="LICENSE.md",
            src=self.source_folder,
            dst=os.path.join(self.package_folder, "licenses"),
        )
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib"))
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "libfn")
        self.cpp_info.set_property("cmake_target_name", "libfn::libfn")

        version = self.cpp_info.components["version"]
        version.set_property("cmake_target_name", "libfn::version")
        version.bindirs = []
        version.libdirs = []

        pfn = self.cpp_info.components["pfn"]
        pfn.set_property("cmake_target_name", "libfn::pfn")
        pfn.bindirs = []
        pfn.libdirs = []
        pfn.requires = ["version"]

        fn = self.cpp_info.components["fn"]
        fn.set_property("cmake_target_name", "libfn::fn")
        fn.bindirs = []
        fn.libdirs = []
        fn.requires = ["pfn", "version"]
        # An option rather than a component, so the libfn::libfn aggregate cannot pull it in
        if self.options.cxx26:
            fn.defines.append("LIBFN_CXX26")
            fn.set_property("cmake_target_aliases", ["libfn::fn_cxx26"])

        # Mirror the INTERFACE options of upstream's cmake/CompilationOptions.cmake
        compiler = self.settings.get_safe("compiler")
        for component in (version, pfn, fn):
            if compiler == "msvc":
                component.cxxflags.append("/permissive-")
                component.defines.append("_HAS_CXX23")
            elif compiler in ("clang", "apple-clang"):
                component.cxxflags.append("-Wno-missing-braces")
