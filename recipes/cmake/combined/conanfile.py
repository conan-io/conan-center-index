import os

from conan import ConanFile
from conan.tools.files import get, copy, rmdir
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout, CMakeDeps
from conan.tools.build import cross_building, check_min_cppstd
from conan.tools.scm import Version
from conan.tools.microsoft import is_msvc
from conan.errors import ConanInvalidConfiguration

required_conan_version = ">=1.51.0"


class CMakeConan(ConanFile):
    name = "cmake"
    package_type = "application"
    description = "CMake, the cross-platform, open-source build system."
    topics = ("build", "installer")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/Kitware/CMake"
    license = "BSD-3-Clause"
    settings = "os", "arch", "compiler", "build_type"

    options = {
        "with_openssl": [True, False],
        "from_sources": [True, False],
    }
    default_options = {
        "with_openssl": True,
        "from_sources": False,
    }

    def set_name(self):
        self.name = os.environ.get('CMAKE_RECIPE_NAME', 'cmake')
        print(self.name)

    def config_options(self):
        if self.settings.os not in ["Macos", "Windows", "Linux"]:
            self.options.from_sources = True
        if self.settings.os == "Windows" and self.options.from_sources:
            self.options.with_openssl = False

    def validate(self):
        if self.options.from_sources:
            self._from_sources_validate()
            return
        if self.settings.arch not in ["x86_64", "armv8"]:
            raise ConanInvalidConfiguration("CMake binaries are only provided for x86_64 and armv8 architectures")

        if self.settings.os == "Windows" and self.settings.arch == "armv8" and Version(self.version) < "3.24":
            raise ConanInvalidConfiguration("CMake only supports ARM64 binaries on Windows starting from 3.24")

    def build(self):
        if self.options.from_sources:
            self._from_sources_build()
            return
        arch = str(self.settings.arch) if self.settings.os != "Macos" else "universal"
        get(self, **self.conan_data["sources"][self.version]["precompiled"][str(self.settings.os)][arch],
            destination=self.source_folder, strip_root=True)

    def package_id(self):
        if self.info.settings.os == "Macos":
            del self.info.settings.arch
        del self.info.settings.compiler
        # The compatibility() method is not compatible with package_id() deleting values from info,
        # so make the packages compatible despite sources or openssl, by deleting those settings.
        # See: https://github.com/conan-io/conan/issues/12476
        del self.info.options.from_sources
        del self.info.options.with_openssl
        # OpenSSL dependency, if used, does not matter for the package ID. Consumers who build from
        # sources will determine if they need OpenSSL or not on an organizational basis.
        self.info.requires.unrelated_mode()

    def package(self):
        if self.options.from_sources:
            self._from_sources_package()
            return
        copy(self, "*", src=self.build_folder, dst=self.package_folder)

        if self.settings.os == "Macos":
            docs_folder = os.path.join(self.build_folder, "CMake.app", "Contents", "doc", "cmake")
        else:
            docs_folder = os.path.join(self.build_folder, "doc", "cmake")

        copy(self, "Copyright.txt", src=docs_folder, dst=os.path.join(self.package_folder, "licenses"), keep_path=False)

        if self.settings.os != "Macos":
            # Remove unneeded folders (also cause long paths on Windows)
            # Note: on macOS we don't want to modify the bundle contents
            #       to preserve signature validation
            rmdir(self, os.path.join(self.package_folder, "doc"))
            rmdir(self, os.path.join(self.package_folder, "man"))

    def package_info(self):
        self.cpp_info.includedirs = []
        self.cpp_info.libdirs = []

        if self.settings.os == "Macos" and not self.options.from_sources:
            bindir = os.path.join(self.package_folder, "CMake.app", "Contents", "bin")
            self.cpp_info.bindirs = [bindir]
        else:
            bindir = os.path.join(self.package_folder, "bin")

        # Needed for compatibility with v1.x - Remove when 2.0 becomes the default
        self.output.info(f"Appending PATH environment variable: {bindir}")
        self.env_info.PATH.append(bindir)

    ##############################################################################
    # Build-from-sources
    ##############################################################################
    def requirements(self):
        if self.options.from_sources and self.options.with_openssl:
            self.requires("openssl/1.1.1t")

    def validate_build(self):
        if not self.options.from_sources:
            return

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

    def _from_sources_validate(self):
        if self.settings.os == "Macos" and self.options.from_sources:
            # On macOS, the downloaded binary is universal, but there's no good way to build a universal
            # binary from sources. Since the settings.arch is deleted from the package_id(), to prevent
            # confusion, only allow downloads.
            raise ConanInvalidConfiguration(
                "This recipe only supports universal binary CMake on macOS, not building from sources")

    def layout(self):
        if not self.options.from_sources:
            return
        cmake_layout(self, src_folder="src")

    def source(self):
        if not self.options.from_sources:
            return
        get(self, **self.conan_data["sources"][self.version]["code"],
            destination=self.source_folder, strip_root=True)
        rmdir(self, os.path.join(self.source_folder, "Tests", "RunCMake", "find_package"))

    def generate(self):
        if not self.options.from_sources:
            return
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

    def _from_sources_build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def _from_sources_package(self):
        copy(self, "Copyright.txt", self.source_folder, os.path.join(self.package_folder, "licenses"), keep_path=False)
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "doc"))
