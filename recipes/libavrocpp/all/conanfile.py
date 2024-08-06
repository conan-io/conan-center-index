from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get, copy, rm, replace_in_file
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.scm import Version
import os

required_conan_version = ">=1.54.0"


class LibavrocppConan(ConanFile):
    name = "libavrocpp"
    description = "Avro is a data serialization system."
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://avro.apache.org/"
    topics = ("serialization", "deserialization","avro")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "fmt/*:header_only": True,
    }
    short_paths = True

    @property
    def _min_cppstd(self):
        # 1.12.0 or later requires C++17 https://github.com/apache/avro/pull/2949
        return "11" if Version(self.version) < "1.12.0" else "17"

    @property
    def _compilers_minimum_version(self):
        return {
            "17": {
                "gcc": "8",
                "clang": "7",
                "apple-clang": "12",
                "Visual Studio": "16",
                "msvc": "192",
            },
        }.get(self._min_cppstd, {})

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if Version(self.version) < "1.12.0":
            # boost upper to 1.81.0 requires C++14 minimum
            self.requires("boost/1.81.0", transitive_headers=True)
        else:
            self.requires("boost/1.85.0", transitive_headers=True)
            self.requires("fmt/10.2.1", transitive_headers=True)
        self.requires("snappy/1.1.9")

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

    def generate(self):
        tc = CMakeToolchain(self)
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)
        cmakelists = os.path.join(self.source_folder, "lang", "c++", "CMakeLists.txt")
        # Fix discovery & link to Snappy
        replace_in_file(self, cmakelists, "SNAPPY_FOUND", "Snappy_FOUND")
        replace_in_file(self, cmakelists, "${SNAPPY_LIBRARIES}", "Snappy::snappy")
        replace_in_file(
            self, cmakelists,
            "target_include_directories(avrocpp_s PRIVATE ${SNAPPY_INCLUDE_DIR})",
            "target_link_libraries(avrocpp_s PRIVATE Snappy::snappy)",
        )
        # Install either static or shared
        target = "avrocpp" if self.options.shared else "avrocpp_s"
        replace_in_file(self, cmakelists, "install (TARGETS avrocpp avrocpp_s" , f"install (TARGETS {target}")

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure(build_script_folder=os.path.join(self.source_folder, "lang", "c++"))
        cmake.build()

    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        copy(self, pattern="NOTICE*", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()

        if self.settings.os == "Windows":
            for dll_pattern_to_remove in ["concrt*.dll", "msvcp*.dll", "vcruntime*.dll"]:
                rm(self, dll_pattern_to_remove, os.path.join(self.package_folder, "bin"))

    def package_info(self):
        self.cpp_info.libs = ["avrocpp"] if self.options.shared else ["avrocpp_s"]
        if self.options.shared:
            self.cpp_info.defines.append("AVRO_DYN_LINK")
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")
        self.cpp_info.requires = [
            "boost::headers", "boost::filesystem", "boost::iostreams", "boost::program_options",
            "boost::regex", "boost::system", "snappy::snappy",
        ]
        if Version(self.version) >= "1.12.0":
            self.cpp_info.requires.append("fmt::fmt")
