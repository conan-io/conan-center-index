from conan import ConanFile
from conan.tools.files import get, copy, load, save
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
import os


required_conan_version = ">=1.53.0"

class LibaesgmConan(ConanFile):
    name = "libaesgm"
    description = "Library implementation of AES (Rijndael) cryptographic methods"
    license = "LicenseRef-libaesgm-BSD"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/xmake-mirror/libaesgm"
    topics = ("aes", "cryptographic")
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

    def export_sources(self):
        copy(self, "CMakeLists.txt", src=self.recipe_folder, dst=self.export_sources_folder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["LIBAESGM_SRC_DIR"] =  self.source_folder.replace("\\", "/")
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure(build_script_folder=os.path.join(self.source_folder, os.pardir))
        cmake.build()

    def package(self):
        filename = os.path.join(self.source_folder, "aes.h")
        file_content = load(self, filename)
        license_end = "*/"
        license_contents = file_content[:file_content.find(license_end)].replace("/*", "")
        save(self, os.path.join(self.package_folder, "licenses", "LICENSE"), license_contents)

        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["Aesgm"]

        self.cpp_info.set_property("cmake_file_name", "Aesgm")
        self.cpp_info.set_property("cmake_target_name", "Aesgm::Aesgm")
