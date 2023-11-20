import os

from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rm, export_conandata_patches, apply_conandata_patches, rmdir, save

required_conan_version = ">=1.53.0"


class PackageConan(ConanFile):
    name = "arbiter"
    description = "Uniform access to the filesystem, HTTP, S3, GCS, Dropbox, etc."
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/connormanning/arbiter"
    topics = ("filesystem", "http", "s3", "gcs", "dropbox")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    @property
    def _min_cppstd(self):
        return 11

    def export_sources(self):
        copy(self, "CMakeLists.txt", self.recipe_folder, self.export_sources_folder)
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
        self.requires("libcurl/[>=7.78.0 <9]")
        self.requires("openssl/[>=1.1 <4]")
        self.requires("zlib/[>=1.2.11 <2]")
        self.requires("nlohmann_json/3.11.2", transitive_headers=True)
        self.requires("rapidxml/1.13", transitive_headers=True)

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.generate()
        tc = CMakeDeps(self)
        tc.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)
        # Unvendor nlohmann_json
        rmdir(self, os.path.join(self.source_folder, "arbiter", "third", "json"))
        save(self, os.path.join(self.source_folder, "arbiter", "third", "json", "json.hpp"),
             "#include <nlohmann/json.hpp>\n")
        # Unvendor rapidxml
        rmdir(self, os.path.join(self.source_folder, "arbiter", "third", "xml"))
        save(self, os.path.join(self.source_folder, "arbiter", "third", "xml", "xml.hpp"),
             "#include <rapidxml/rapidxml.hpp>\n"
             "namespace Xml = rapidxml;\n")


    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure(build_script_folder=self.source_path.parent)
        cmake.build()

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        copy(self, "*.hpp",
             os.path.join(self.source_folder, "arbiter"),
             os.path.join(self.package_folder, "include", "arbiter"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "lib"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "bin"))

    def package_info(self):
        self.cpp_info.libs = ["arbiter"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("pthread")
        elif self.settings.os == "Windows":
            self.cpp_info.system_libs.append("Shlwapi")
        if self.options.shared:
            self.cpp_info.defines.append("ARBITER_DLL_IMPORT")
