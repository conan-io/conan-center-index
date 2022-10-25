from conan import ConanFile, conan_version
from conan.tools.files import chdir, copy, rmdir, replace_in_file
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout
from conan.tools.gnu import AutotoolsToolchain, Autotools
from conan.tools.build import build_jobs, cross_building, check_min_cppstd
from conan.tools.scm import Version
from conan.errors import ConanInvalidConfiguration
from conan.errors import ConanException
import os

required_conan_version = ">=1.52.0"

class CMakeConan(ConanFile):
    name = "cmake"
    package_type = "application"
    description = "Conan installer for CMake"
    topics = ("cmake", "build", "installer")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/Kitware/CMake"
    license = "BSD-3-Clause"
    settings = "os", "arch", "compiler", "build_type"

    options = {
        "with_openssl": [True, False],
        "bootstrap": [True, False],
    }
    default_options = {
        "with_openssl": True,
        "bootstrap": False,
    }

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.with_openssl = False

    def requirements(self):
        if self.options.with_openssl:
            self.requires("openssl/1.1.1q")

    def validate(self):
        if self.info.settings.os == "Macos" and self.info.settings.arch == "x86":
            raise ConanInvalidConfiguration("CMake does not support x86 for macOS")

        if self.info.settings.os == "Windows" and self.info.options.bootstrap:
            raise ConanInvalidConfiguration("CMake does not support bootstrapping on Windows")

        minimal_cpp_standard = "11"
        if self.info.settings.get_safe("compiler.cppstd"):
            check_min_cppstd(self, minimal_cpp_standard)

        minimal_version = {
            "gcc": "4.8",
            "clang": "3.3",
            "apple-clang": "9",
            "Visual Studio": "14",
        }

        compiler = str(self.info.settings.compiler)
        if compiler not in minimal_version:
            self.output.warning(
                "{} recipe lacks information about the {} compiler standard version support".format(self.name, compiler))
            self.output.warning(
                "{} requires a compiler that supports at least C++{}".format(self.name, minimal_cpp_standard))
            return

        version = Version(self.info.settings.compiler.version)
        if version < minimal_version[compiler]:
            raise ConanInvalidConfiguration(
                "{} requires a compiler that supports at least C++{}".format(self.name, minimal_cpp_standard))

    def layout(self):
        cmake_layout(self, src_folder="src")
    
    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)
    
    def generate(self):
        if self.info.options.bootstrap:
            tc = AutotoolsToolchain(self)
            tc.generate()
        else:
            tc = CMakeToolchain(self)
            if not self.settings.compiler.cppstd:
                tc.variables["CMAKE_CXX_STANDARD"] = 11
            tc.variables["CMAKE_BOOTSTRAP"] = False
            if self.settings.os == "Linux":
                tc.variables["CMAKE_USE_OPENSSL"] = self.options.with_openssl
                if self.options.with_openssl:
                    openssl = self.dependencies["openssl"]
                    tc.variables["OPENSSL_USE_STATIC_LIBS"] = not openssl.options.shared
            if cross_building(self):
                tc.variables["HAVE_POLL_FINE_EXITCODE"] = ''
                tc.variables["HAVE_POLL_FINE_EXITCODE__TRYRUN_OUTPUT"] = ''
            tc.generate()

    def build(self):
        if self.info.options.bootstrap:
            with chdir(self, self.source_folder):
                self.run('./bootstrap --prefix="" --parallel={}'.format(build_jobs(self)))
                autotools = Autotools(self)
                autotools.make()
        else:
            if self.settings.os == "Linux":
                replace_in_file(self, os.path.join(self.source_folder, "Utilities", "cmcurl", "CMakeLists.txt"),
                                      "list(APPEND CURL_LIBS ${OPENSSL_LIBRARIES})",
                                      "list(APPEND CURL_LIBS ${OPENSSL_LIBRARIES} ${CMAKE_DL_LIBS} pthread)")
            cmake = CMake(self)
            cmake.configure()
            cmake.build()

    def package(self):
        copy(self, "Copyright.txt", self.source_folder, os.path.join(self.package_folder, "licenses"), keep_path=False)
        if self.options.bootstrap:
            with chdir(self, self.source_folder):
                autotools = Autotools(self)
                autotools.install()
        else:
            cmake = CMake(self)
            cmake.configure()
            cmake.install()
        rmdir(self, os.path.join(self.package_folder, "doc"))

    def package_id(self):
        del self.info.settings.compiler

    def package_info(self):
        self.buildenv_info.prepend_path("CMAKE_ROOT", self.package_folder)
        self.runenv_info.define_path("CMAKE_ROOT", self.package_folder)
        module_version = "{}.{}".format(Version(self.version).major, Version(self.version).minor)
        mod_path = os.path.join(self.package_folder, "share", f"cmake-{module_version}", "Modules")
        self.buildenv_info.prepend_path("CMAKE_MODULE_PATH", mod_path)
        self.runenv_info.define_path("CMAKE_MODULE_PATH", mod_path)
        if not os.path.exists(mod_path):
            raise ConanException("Module path not found: %s" % mod_path)

        self.cpp_info.includedirs = []
        
        # TODO remove once conan v2 is the only support and recipes have been migrated
        if Version(conan_version).major < 2:
            bindir = os.path.join(self.package_folder, "bin")
            self.output.info("Appending PATH environment variable: {}".format(bindir))
            self.runenv_info.append_path("PATH", bindir)
