import os
import re
import shlex

from conan import ConanFile
from conan.errors import ConanException
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.env import Environment
from conan.tools.files import apply_conandata_patches, chdir, copy, export_conandata_patches, get, load, replace_in_file, rmdir, save
from conan.tools.gnu import Autotools, AutotoolsToolchain, PkgConfigDeps
from conan.tools.microsoft import is_msvc, unix_path

required_conan_version = ">=1.53.0"


class LibUSBCompatConan(ConanFile):
    name = "libusb-compat"
    description = "A compatibility layer allowing applications written for libusb-0.1 to work with libusb-1.0"
    license = ("LGPL-2.1", "BSD-3-Clause")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/libusb/libusb-compat-0.1"
    topics = ("libusb", "compatibility", "usb")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "enable_logging": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "enable_logging": False,
    }

    @property
    def _settings_build(self):
        return self.settings_build if hasattr(self, "settings_build") else self.settings

    def export_sources(self):
        export_conandata_patches(self)
        copy(self, "CMakeLists.txt.in", src=self.recipe_folder, dst=self.export_sources_folder)

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

    def requirements(self):
        self.requires("libusb/1.0.26")
        if is_msvc(self):
            self.requires("dirent/1.24", transitive_headers=True, transitive_libs=True)

    def build_requirements(self):
        self.tool_requires("gnu-config/cci.20210814")
        self.tool_requires("libtool/2.4.7")
        if not self.conf.get("tools.gnu:pkg_config", default=False, check_type=str):
            self.tool_requires("pkgconf/2.0.3")
        if self._settings_build.os == "Windows":
            self.win_bash = True
            if not self.conf.get("tools.microsoft.bash:path", check_type=str):
                self.tool_requires("msys2/cci.latest")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def _iterate_lib_paths_win(self, lib):
        """Return all possible library paths for lib"""
        libdirs = sum([dep.cpp_info.libdirs for dep in self.dependencies.values()], [])
        for lib_path in libdirs:
            for prefix in "", "lib":
                for suffix in "", ".a", ".dll.a", ".lib", ".dll.lib":
                    fn = os.path.join(lib_path, f"{prefix}{lib}{suffix}")
                    if not fn.endswith(".a") and not fn.endswith(".lib"):
                        continue
                    yield fn

    @property
    def _absolute_dep_libs_win(self):
        libs = sum([dep.cpp_info.libs for dep in self.dependencies.values()], [])
        absolute_libs = []
        for lib in libs:
            for fn in self._iterate_lib_paths_win(lib):
                if not os.path.isfile(fn):
                    continue
                absolute_libs.append(fn)
                break
        return absolute_libs

    def generate(self):
        tc = CMakeToolchain(self)
        tc.generate()
        tc = CMakeDeps(self)
        tc.generate()
        tc = PkgConfigDeps(self)
        tc.generate()

        tc = AutotoolsToolchain(self)
        if is_msvc(self):
            # Use absolute paths of the libraries instead of the library names only.
            # Otherwise, the configure script will say that the compiler not working
            # (because it interprets the libs as input source files)
            tc.libs = list(unix_path(self, l) for l in self._absolute_dep_libs_win)
            tc.libs += sum([dep.cpp_info.system_libs for dep in self.dependencies.values()], [])
        tc.configure_args += [
            "--disable-examples-build",
            "--enable-log" if self.options.enable_logging else "--disable-log",
        ]
        tc.generate()

        if is_msvc(self):
            env = Environment()
            automake_conf = self.dependencies.build["automake"].conf_info
            compile_wrapper = unix_path(self, automake_conf.get("user.automake:compile-wrapper", check_type=str))
            ar_wrapper = unix_path(self, automake_conf.get("user.automake:lib-wrapper", check_type=str))
            env.define("CC", f"{compile_wrapper} cl -nologo")
            env.define("CXX", f"{compile_wrapper} cl -nologo")
            env.define("LD", "link -nologo")
            env.define("AR", f'{ar_wrapper} "lib -nologo"')
            env.define("NM", "dumpbin -symbols")
            env.define("OBJDUMP", ":")
            env.define("RANLIB", ":")
            env.define("STRIP", ":")
            env.vars(self).save_script("conanbuild_msvc")

    def _extract_makefile_variable(self, makefile, variable):
        makefile_contents = load(self, makefile)
        match = re.search(
            fr'^{variable}\s*=\s*((?:[\w \t.=/-]|\")*(?:\\\n(?:[\w \t.=/-]|\")*)*)$',
            makefile_contents,
            flags=re.MULTILINE,
        )
        if not match:
            raise ConanException(f"Cannot extract variable {variable} from {makefile_contents}")
        lines = [line.strip(" \t\\") for line in match.group(1).split()]
        return [item for line in lines for item in shlex.split(line) if item]

    def _extract_autotools_variables(self):
        makefile = os.path.join(self.source_folder, "libusb", "Makefile.am")
        sources = self._extract_makefile_variable(makefile, "libusb_la_SOURCES")
        headers = self._extract_makefile_variable(makefile, "include_HEADERS")
        return sources, headers

    def _patch_sources(self):
        apply_conandata_patches(self)
        for gnu_config in [
            self.conf.get("user.gnu-config:config_guess", check_type=str),
            self.conf.get("user.gnu-config:config_sub", check_type=str),
        ]:
            if gnu_config:
                copy(self, os.path.basename(gnu_config),
                     src=os.path.dirname(gnu_config),
                     dst=self.source_folder)
        if self.settings.os == "Windows":
            api = "__declspec(dllexport)" if self.options.shared else ""
            replace_in_file(
                self,
                os.path.join(self.source_folder, "configure.ac"),
                "\nAC_DEFINE([API_EXPORTED]",
                f"\nAC_DEFINE([API_EXPORTED], [{api}], [API])\n#",
            )
            # libtool disallows building shared libraries that link to static libraries
            # This will override this and add the dependency
            replace_in_file(
                self,
                os.path.join(self.source_folder, "ltmain.sh"),
                "droppeddeps=yes",
                'droppeddeps=no && func_append newdeplibs " $a_deplib"',
            )

    def build(self):
        self._patch_sources()
        with chdir(self, self.source_folder):
            autotools = Autotools(self)
            autotools.autoreconf()
            autotools.configure()
        if self.settings.os == "Windows":
            cmakelists_in = load(self, os.path.join(self.export_sources_folder, "CMakeLists.txt.in"))
            sources, headers = self._extract_autotools_variables()
            save(self, os.path.join(self.source_folder, "libusb", "CMakeLists.txt"), cmakelists_in.format(
                libusb_sources=" ".join(sources),
                libusb_headers=" ".join(headers),
            ))
            replace_in_file(self, os.path.join(self.source_folder, "config.h"),
                            "\n#define API_EXPORTED", "\n#define API_EXPORTED //")
            copy(self, "config.h", self.source_folder, os.path.join(self.source_folder, "libusb"))
            cmake = CMake(self)
            cmake.configure(build_script_folder=os.path.join(self.source_folder, "libusb"))
            cmake.build()
        else:
            with chdir(self, self.source_folder):
                autotools.make()

    def package(self):
        copy(self, "LICENSE",
             src=self.source_folder,
             dst=os.path.join(self.package_folder, "licenses"))
        if self.settings.os == "Windows":
            cmake = CMake(self)
            cmake.install()
        else:
            with chdir(self, self.source_folder):
                autotools = Autotools(self)
                autotools.install()
            os.unlink(os.path.join(self.package_folder, "bin", "libusb-config"))
            os.unlink(os.path.join(self.package_folder, "lib", "libusb.la"))
            rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
            fix_apple_shared_install_name(self)

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "libusb")
        self.cpp_info.libs = ["usb"]
        if not self.options.shared:
            self.cpp_info.defines = ["LIBUSB_COMPAT_STATIC"]
