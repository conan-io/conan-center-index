import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir

required_conan_version = ">=2.1"


class ApibrasilConan(ConanFile):
    name = "apibrasil"
    description = (
        "Official C++ SDK for the APIBrasil platform - WhatsApp, SMS, "
        "CPF/CNPJ lookups, vehicles, CEP, correios, PIX/boleto payments and more."
    )
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/APIBrasil/apigratis-sdk-cpp"
    topics = ("apibrasil", "whatsapp", "sms", "cpf-cnpj", "pix", "sdk")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_curl": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_curl": True,
    }

    @property
    def _min_cppstd(self):
        return 17

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
            # Windows ships a native WinHTTP transport, so libcurl is optional there.
            self.options.with_curl = False

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        # nlohmann/json is exposed through the SDK's public headers.
        self.requires("nlohmann_json/3.11.3", transitive_headers=True)
        if self.options.with_curl:
            self.requires("libcurl/[>=7.78.0 <9]")

    def validate(self):
        check_min_cppstd(self, self._min_cppstd)
        if self.settings.os != "Windows" and not self.options.with_curl:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires with_curl=True on non-Windows platforms; "
                "libcurl is the only HTTP transport there (Windows uses WinHTTP)."
            )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        deps = CMakeDeps(self)
        deps.generate()
        tc = CMakeToolchain(self)
        tc.variables["APIBRASIL_BUILD_EXAMPLES"] = False
        tc.variables["APIBRASIL_BUILD_TESTS"] = False
        tc.variables["APIBRASIL_INSTALL"] = True
        if not self.options.with_curl:
            # Keep CMake from picking up a system libcurl and selecting the wrong
            # transport; without curl in the graph only WinHTTP remains.
            tc.variables["CMAKE_DISABLE_FIND_PACKAGE_CURL"] = True
        if self.options.get_safe("shared"):
            # The library does not annotate its API with dllexport, so let CMake
            # export all symbols when building a Windows DLL.
            tc.variables["CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS"] = True
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE",
             src=self.source_folder,
             dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        # The project ships its own *Config.cmake; on Conan the consumer's
        # CMakeDeps generates those, so drop the packaged ones to avoid conflicts.
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.libs = ["apibrasil"]
        self.cpp_info.set_property("cmake_file_name", "apibrasil")
        self.cpp_info.set_property("cmake_target_name", "apibrasil::apibrasil")

        self.cpp_info.requires = ["nlohmann_json::nlohmann_json"]
        if self.options.with_curl:
            self.cpp_info.requires.append("libcurl::libcurl")
            self.cpp_info.defines.append("APIBRASIL_HAVE_CURL")
        if self.settings.os == "Windows":
            self.cpp_info.system_libs.append("winhttp")
            self.cpp_info.defines.append("APIBRASIL_HAVE_WINHTTP")
