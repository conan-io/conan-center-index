from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os
from conan.tools.build import cross_building
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rmdir
import os


required_conan_version = ">=1.54.0"

class PackageConan(ConanFile):
    name = "git"
    description = "Fast, scalable, distributed revision control system"
    license = "GPL-2.0-only"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://git-scm.com/"
    topics = ("scm", "version-control")
    package_type = "application"
    settings = "os", "arch", "compiler", "build_type"

    def configure(self):
        # C only
        self.settings.compiler.rm_safe("libcxx")
        self.settings.compiler.rm_safe("cppstd")

    def layout(self):
        cmake_layout(self, src_folder="src")
    
    def export_sources(self):
        export_conandata_patches(self)
    
    def validate(self):
        if cross_building(self):
            raise ConanInvalidConfiguration(f"FIXME: {self.ref} (currently) does not support cross building.")

    def requirements(self):
        self.requires("expat/[>=2.6.2 <3]")
        self.requires("libcurl/[>=7.78.0 <9]")
        self.requires("libiconv/1.17")
        self.requires("openssl/[>=1.1 <4]")
        self.requires("zlib/[>=1.2.11 <2]")
        if self.settings.os != "Windows":
            # Git's CMake tries to pick this up only when PkgConfig is detected, so it
            # likely expects it to not exist on Windows. It fails if it is injected.
            self.requires("pcre2/10.43")

    def build_requirements(self):
        self.tool_requires("gettext/0.22.5")
    
    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_TESTING"] = False
        # So `check_c_source_compiles` can work with multi-config generators
        tc.variables["CMAKE_TRY_COMPILE_CONFIGURATION"] = self.settings.build_type
        if is_apple_os(self):
            # This isn't set properly in CMake.
            # https://lore.kernel.org/git/1236547371-88742-1-git-send-email-benji@silverinsanity.com/T/
            tc.preprocessor_definitions["USE_ST_TIMESPEC"] = "1"
            # Forces Git to look relative to the binary for additional files.
            tc.preprocessor_definitions["RUNTIME_PREFIX"] = "1"
            # Allows the use of _NSGetExecutablePath to get the path of the running executable,
            # used in tandem with RUNTIME_PREFIX.
            tc.preprocessor_definitions["HAVE_NS_GET_EXECUTABLE_PATH"] = "1"
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        apply_conandata_patches(self)

        cmake_directory = os.path.join(self.source_folder, "contrib", "buildsystems")

        cmake = CMake(self)
        cmake.configure(
            build_script_folder=cmake_directory,
            # USE_VCPKG is checked before project(), so it can't be injected from the toolchain.
            cli_args=["-DUSE_VCPKG=OFF"],
        )
        cmake.build()

    def package(self):
        copy(self, "COPYING", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        # Contains mainly perl scripts an examples, otherwise is actually rather small
        rmdir(self, os.path.join(self.package_folder, "share"))
        # Contains many executables which are near duplicates of `git`, presumably with pre-configured command line args.
        # Greatly bloats the package size. These are also packaged on normal distributions, but often separately. Unsure of their purpose.
        rmdir(self, os.path.join(self.package_folder, "libexec"))

    def package_id(self):
        # Just an application
        del self.info.settings.compiler

    def package_info(self):
        self.cpp_info.frameworkdirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.resdirs = []
        self.cpp_info.includedirs = []

        bin_folder = os.path.join(self.package_folder, "bin")

        self.runenv_info.prepend_path("PATH", bin_folder)

        # TODO: Legacy, to be removed in Conan 2.0
        self.env_info.PATH.append(bin_folder)
