from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rm, rmdir, replace_in_file
from conan.tools.microsoft import is_msvc, is_msvc_static_runtime
from conan.tools.scm import Version
import os


required_conan_version = ">=2.0.9"

class PackageConan(ConanFile):
    name = "cpp-smtpclient-library"
    description = "An SMTP client library built in C++ that support authentication and secure connections"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/jeremydumais/CPP-SMTPClient-library"
    topics = ("c", "cpp", "cpp-library", "macos", "windows", "linux", "smtp", "email")
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

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("openssl/[>=1.1 <4]")

    def validate(self):
        check_min_cppstd(self, 14)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"), "${OPENSSL_CRYPTO_LIBRARY} ${OPENSSL_SSL_LIBRARY}", "OpenSSL::Crypto OpenSSL::SSL")
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"), "ssl crypto", "OpenSSL::Crypto OpenSSL::SSL")

    def generate(self):
        tc = CMakeToolchain(self)
        if is_msvc(self):
            tc.cache_variables["USE_MSVC_RUNTIME_LIBRARY_DLL"] = not is_msvc_static_runtime(self)
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
        # For <=1.1.11 the libs were under lib/smtpclient
        if Version(self.version) < "1.1.12":
            self.cpp_info.libdirs = [os.path.join("lib", "smtpclient")]
        # For 1.1.12+ use the default ("lib"), so no override needed.
        self.cpp_info.libs = ["smtpclient"]
        self.cpp_info.set_property("cmake_module_file_name", "smtpclient")
        self.cpp_info.set_property("cmake_module_target_name", "smtpclient::smtpclient")
        self.cpp_info.set_property("cmake_file_name", "smtpclient")
        self.cpp_info.set_property("cmake_target_name", "smtpclient::smtpclient")
        if not self.options.shared:
            self.cpp_info.defines.append("SMTPCLIENT_STATIC")
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["m", "pthread", "dl"])
