from conan import ConanFile
from conan.tools.files import chdir, copy, rmdir, get, save, load
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout, CMakeDeps
from conan.tools.gnu import Autotools, AutotoolsToolchain, AutotoolsDeps
from conan.tools.layout import basic_layout
from conan.tools.build import build_jobs, cross_building, check_min_cppstd
from conan.tools.scm import Version
from conan.tools.microsoft import is_msvc
from conan.errors import ConanInvalidConfiguration

import os
import json

required_conan_version = ">=1.51.0"

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
        if self.options.get_safe("with_openssl", default=False):
            self.requires("openssl/[>=1.1 <4]")

    def validate_build(self):
        if self.settings.os == "Windows" and self.options.bootstrap:
            raise ConanInvalidConfiguration("CMake does not support bootstrapping on Windows")

        minimal_cpp_standard = "11"
        if self.settings.get_safe("compiler.cppstd"):
            check_min_cppstd(self, minimal_cpp_standard)

        minimal_version = {
            "gcc": "4.8",
            "clang": "3.3",
            "apple-clang": "9",
            "Visual Studio": "14",
            "msvc": "190",
        }

        compiler = str(self.settings.compiler)
        if compiler not in minimal_version:
            self.output.warning(
                f"{self.name} recipe lacks information about the {compiler} compiler standard version support")
            self.output.warning(
                f"{self.name} requires a compiler that supports at least C++{minimal_cpp_standard}")
            return

        version = Version(self.settings.compiler.version)
        if version < minimal_version[compiler]:
            raise ConanInvalidConfiguration(
                f"{self.name} requires a compiler that supports at least C++{minimal_cpp_standard}")

    def validate(self):
        if self.settings.os == "Macos" and self.settings.arch == "x86":
            raise ConanInvalidConfiguration("CMake does not support x86 for macOS")

    def layout(self):
        if self.options.bootstrap:
            basic_layout(self, src_folder="src")
        else:
            cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)
        rmdir(self, os.path.join(self.source_folder, "Tests", "RunCMake", "find_package"))

    def generate(self):
        if self.options.bootstrap:
            tc = AutotoolsToolchain(self)
            tc.generate()
            tc = AutotoolsDeps(self)
            tc.generate()
            bootstrap_cmake_options = ["--"]
            bootstrap_cmake_options.append(f'-DCMAKE_CXX_STANDARD={"11" if not self.settings.compiler.cppstd else self.settings.compiler.cppstd}')
            if self.settings.os == "Linux":
                if self.options.with_openssl:
                    openssl = self.dependencies["openssl"]
                    bootstrap_cmake_options.append("-DCMAKE_USE_OPENSSL=ON")
                    bootstrap_cmake_options.append(f'-DOPENSSL_USE_STATIC_LIBS={"FALSE" if openssl.options.shared else "TRUE"}')
                    bootstrap_cmake_options.append(f'-DOPENSSL_ROOT_DIR={openssl.package_path}')
                else:
                    bootstrap_cmake_options.append("-DCMAKE_USE_OPENSSL=OFF")
            save(self, "bootstrap_args", json.dumps({"bootstrap_cmake_options": ' '.join(arg for arg in bootstrap_cmake_options)}))
        else:
            tc = CMakeToolchain(self)
            # Disabling testing because CMake tests build can fail in Windows in some cases
            tc.variables["BUILD_TESTING"] = False
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
            # TODO: Remove after fixing https://github.com/conan-io/conan-center-index/issues/13159
            # C3I workaround to force CMake to choose the highest version of
            # the windows SDK available in the system
            if is_msvc(self) and not self.conf.get("tools.cmake.cmaketoolchain:system_version"):
                tc.variables["CMAKE_SYSTEM_VERSION"] = "10.0"
            tc.generate()
            tc = CMakeDeps(self)
            # CMake try_compile failure: https://github.com/conan-io/conan-center-index/pull/16073#discussion_r1110037534
            tc.set_property("openssl", "cmake_find_mode", "module")
            tc.generate()


    def build(self):
        if self.options.bootstrap:
            toolchain_file_content = json.loads(load(self, os.path.join(self.generators_folder, "bootstrap_args")))
            bootstrap_cmake_options = toolchain_file_content.get("bootstrap_cmake_options")
            with chdir(self, self.source_folder):
                self.run(f'./bootstrap --prefix="" --parallel={build_jobs(self)} {bootstrap_cmake_options}')
                autotools = Autotools(self)
                autotools.make()
        else:
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
            cmake.install()
        rmdir(self, os.path.join(self.package_folder, "doc"))

    def package_id(self):
        del self.info.settings.compiler
        del self.info.options.bootstrap

    def package_info(self):
        self.cpp_info.includedirs = []
        self.cpp_info.libdirs = []

        # Needed for compatibility with v1.x - Remove when 2.0 becomes the default
        bindir = os.path.join(self.package_folder, "bin")
        self.output.info(f"Appending PATH environment variable: {bindir}")
        self.env_info.PATH.append(bindir)
