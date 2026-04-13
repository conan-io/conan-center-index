from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rm, rmdir
from conan.tools.microsoft import is_msvc
import os


required_conan_version = ">=2.0.9"


class TextmatelibConan(ConanFile):
    name = "textmatelib"
    description = "C++ implementation of TextMate grammar parsing and tokenization for syntax highlighting"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/jbltx/TextMateLib"
    topics = ("textmate", "syntax-highlighting", "grammar", "tokenizer", "parsing")
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
    implements = ["auto_shared_fpic"]

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("oniguruma/6.9.9", transitive_headers=True, transitive_libs=True)
        self.requires("rapidjson/cci.20250205", transitive_headers=True)

    def validate(self):
        check_min_cppstd(self, 17)
        if is_msvc(self) and self.options.shared:
            raise ConanInvalidConfiguration(
                f"{self.ref} cannot be built as shared with MSVC."
            )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        apply_conandata_patches(self)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["USE_WASM_BUILD"] = False
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        rm(self, "*.pdb", self.package_folder, recursive=True)

    def package_info(self):
        self.cpp_info.libs = ["tml"]
        self.cpp_info.set_property("cmake_file_name", "TextMateLib")
        self.cpp_info.set_property("cmake_target_name", "TextMateLib::tml")

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("pthread")