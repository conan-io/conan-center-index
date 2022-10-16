from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import copy, get, replace_in_file, rm, rmdir
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.microsoft import unix_path
import os
import shutil

required_conan_version = ">=1.50.0"


class LibelfConan(ConanFile):
    name = "libelf"
    description = "ELF object file access library"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://directory.fsf.org/wiki/Libelf"
    license = "LGPL-2.0"
    topics = ("elf", "fsf", "libelf", "object-file")

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    exports_sources = "CMakeLists.txt"

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    @property
    def _user_info_build(self):
        return getattr(self, "user_info_build", self.deps_user_info)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            try:
                del self.options.fPIC
            except Exception:
                pass
        try:
            del self.settings.compiler.libcxx
        except Exception:
            pass
        try:
            del self.settings.compiler.cppstd
        except Exception:
            pass

    def layout(self):
        if self.settings.os == "Windows":
            cmake_layout(self, src_folder="src")
        else:
            basic_layout(self, src_folder="src")

    def validate(self):
        if self.info.options.shared and self.info.settings.os not in ["Linux", "FreeBSD", "Windows"]:
            raise ConanInvalidConfiguration("libelf can not be built as shared library on non linux/FreeBSD/windows platforms")

    def build_requirements(self):
        if self.settings.os != "Windows":
            self.tool_requires("autoconf/2.71")
            self.tool_requires("gnu-config/cci.20210814")
            if self._settings_build.os == "Windows":
                self.win_bash = True
                if not self.conf.get("tools.microsoft.bash:path", default=False, check_type=bool):
                    self.tool_requires("msys2/cci.latest")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        if self.settings.os == "Windows":
            tc = CMakeToolchain(self)
            tc.variables["LIBELF_SRC_DIR"] = self.source_folder.replace("\\", "/")
            tc.generate()
        else:
            env = VirtualBuildEnv(self)
            env.generate()
            tc = AutotoolsToolchain(self)
            tc.configure_args.extend([
                # it's required, libelf doesnt seem to understand DESTDIR
                f"--prefix={self.package_folder}",
            ])
            tc.generate()

    def build(self):
        if self.settings.os == "Windows":
            cmake = CMake(self)
            cmake.configure(build_script_folder=os.path.join(self.source_folder, os.pardir))
            cmake.build()
        else:
            replace_in_file(self, os.path.join(self.source_folder, "lib", "Makefile.in"),
                                  "$(LINK_SHLIB)",
                                  "$(LINK_SHLIB) $(LDFLAGS)")
            # libelf sources contains really outdated 'config.sub' and
            # 'config.guess' files. It not allows to build libelf for armv8 arch.
            shutil.copy(self._user_info_build["gnu-config"].CONFIG_SUB,
                        os.path.join(self.source_folder, "config.sub"))
            shutil.copy(self._user_info_build["gnu-config"].CONFIG_GUESS,
                        os.path.join(self.source_folder, "config.guess"))
            autotools = Autotools(self)
            autotools.autoreconf()
            autotools.configure()
            autotools.make()

    def package(self):
        copy(self, "COPYING.LIB", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        if self.settings.os == "Windows":
            cmake = CMake(self)
            cmake.install()
        else:
            autotools = Autotools(self)
            # TODO: replace by autotools.install() once https://github.com/conan-io/conan/issues/12153 fixed
            autotools.install(args=[f"DESTDIR={unix_path(self, self.package_folder)}"])
            rmdir(self, os.path.join(self.package_folder, "lib", "locale"))
            if self.options.shared:
                rm(self, "*.a", os.path.join(self.package_folder, "lib"))
            rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
            rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "libelf")
        self.cpp_info.libs = ["elf"]
        self.cpp_info.includedirs.append(os.path.join("include", "libelf"))
