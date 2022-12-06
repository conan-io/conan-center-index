from conan import ConanFile
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get, rm, replace_in_file
from conan.tools.scm import Version
from conans import CMake
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.52.0"


class DoxygenConan(ConanFile):
    name = "doxygen"
    description = "A documentation system for C++, C, Java, IDL and PHP --- Note: Dot is disabled in this package"
    topics = ("doxygen", "installer", "devtool", "documentation")
    homepage = "https://github.com/doxygen/doxygen"
    license = "GPL-2.0-or-later"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "enable_parse": [True, False],
        "enable_search": [True, False],
    }
    default_options = {
        "enable_parse": True,
        "enable_search": True,
    }
    generators = "cmake", "cmake_find_package"

    def export_sources(self):
        export_conandata_patches(self)

    def _minimum_compiler_version(self):
        if Version(self.version) <= "1.9.1":
            return {
                "gcc": 5,
            }.get(str(self.settings.compiler))
        elif Version(self.version) <= "1.9.4":
            return {
                "gcc": 7,  # https://gcc.gnu.org/bugzilla/show_bug.cgi?id=66297
                "Visual Studio": 15,
            }.get(str(self.settings.compiler))
        else:
            return {
                "gcc": 7,  # https://gcc.gnu.org/bugzilla/show_bug.cgi?id=66297
                "Visual Studio": 16,
            }.get(str(self.settings.compiler))

    def configure(self):
        del self.settings.compiler.cppstd

    def requirements(self):
        if self.options.enable_search:
            self.requires("xapian-core/1.4.19")
            self.requires("zlib/1.2.13")

    def build_requirements(self):
        if self.settings.os == "Windows":
            self.build_requires("winflexbison/2.5.24")
        else:
            self.build_requires("flex/2.6.4")
            self.build_requires("bison/3.8.2")

    def validate(self):
        minimum_compiler_version = self._minimum_compiler_version()
        if minimum_compiler_version is not None:
            if Version(self.settings.compiler.version) < minimum_compiler_version:
                raise ConanInvalidConfiguration(f"Compiler version too old. At least {minimum_compiler_version} is required.")
        if (self.settings.compiler == "Visual Studio" and
                Version(self.settings.compiler.version) <= "14" and
                Version(self.version) == "1.8.18"):
            raise ConanInvalidConfiguration(f"Doxygen version {self.version} broken with VS {self.settings.compiler.version}.")

    def package_id(self):
        del self.info.settings.compiler

        # Doxygen doesn't make code. Any package that will run is ok to use.
        # It's ok in general to use a release version of the tool that matches the
        # build os and architecture.
        compatible_pkg = self.info.clone()
        compatible_pkg.settings.build_type = "Release"
        self.compatible_packages.append(compatible_pkg)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def build(self):
        if os.path.isfile("Findflex.cmake"):
            os.unlink("Findflex.cmake")
        if os.path.isfile("Findbison.cmake"):
            os.unlink("Findbison.cmake")
        apply_conandata_patches(self)
        if Version(self.version) < "1.9.0":
            replace_in_file(self, "addon/doxysearch/CMakeLists.txt",
                            "find_package(Xapian REQUIRED)", "find_package(xapian REQUIRED)")
            replace_in_file(self, "addon/doxysearch/CMakeLists.txt",
                            "\"uuid.lib rpcrt4.lib ws2_32.lib\"", "uuid.lib rpcrt4.lib ws2_32.lib")
            rm(self, "FindXapian.cmake", "cmake")
        cmake = CMake(self)
        cmake.definitions["build_parse"] = self.options.enable_parse
        cmake.definitions["build_search"] = self.options.enable_search
        cmake.configure()
        cmake.build()

    def package(self):
        self.copy("LICENSE", src=self.source_folder, dst="licenses")
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libdirs = []
        self.cpp_info.includedirs = []
        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info(f"Appending PATH environment variable: {bin_path}")
        self.env_info.PATH.append(bin_path)
