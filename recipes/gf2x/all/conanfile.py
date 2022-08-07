from conans import ConanFile, tools, AutoToolsBuildEnvironment
import contextlib
import shutil
from conan.errors import ConanInvalidConfiguration
from conan.tools.env import VirtualBuildEnv
from conan.tools.microsoft import is_msvc
from conan.tools.files import get, rmdir, copy, chdir
from conan.tools.scm import Version
from conan.tools.build import cross_building
import os

required_conan_version = ">=1.43.0"

class Gf2xConan(ConanFile):
    name = "gf2x"
    license = "LGPL-2.1"
    homepage = "https://gitlab.inria.fr/gf2x/gf2x"
    url = "https://github.com/conan-io/conan-center-index"
    description = "gf2x is a C/C++ software package containing routines for fast arithmetic in GF(2)[x] (multiplication, squaring, GCD) and searching for irreducible/primitive trinomials."
    topics = ("math", "arithmetic")
    settings = "os", "compiler", "build_type", "arch"
    exports_sources = ["patches/**"]
    generators = "cmake", "cmake_find_package"

    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "hardware_specific_code": [True, False],
        "sse2": [True, False],
        "sse3":  [True, False],
        "ssse3":  [True, False],
        "sse41":  [True, False],
        "pclmul":  [True, False],
        "fft_interface":  [True, False]
    }

    default_options = {
        "shared": False,
        "fPIC": True,
        "hardware_specific_code": True,
        "sse2": True,
        "sse3":  True,
        "ssse3":  True,
        "sse41":  True,
        "pclmul":  True,
        "fft_interface":  False
    }

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def source(self):
        get(self, **self.conan_data["sources"][self.version], destination=self._source_subfolder, strip_root=True)

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def config_options(self):
        if self.settings.compiler in ("clang", "apple-clang"):
            raise ConanInvalidConfiguration("Clang compilers not supported")

        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def build_requirements(self):
        if self._settings_build.os == "Windows" and not tools.get_env("CONAN_BASH_PATH"):
            self.build_requires("msys2/cci.latest")

        if self._settings_build.os == "Windows":
            self.build_requires("strawberryperl/5.30.0.1")

        self.build_requires("m4/1.4.19")
        self.build_requires("autoconf/2.71")
        self.build_requires("libtool/2.4.7")
            
        if is_msvc(self):
            self.build_requires("yasm/1.3.0")
            self.build_requires("automake/1.16.5")

    def _configure_autotools(self):
        with chdir(self, self._source_subfolder):
            self.run(
                "{} --install".format(os.environ["AUTORECONF"]),
                win_bash=tools.os_info.is_windows,
                run_environment=True
            )

        yes_no = lambda v: "yes" if v else "no"
        autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        configure_args = [
            "--with-pic={}".format(yes_no(self.options.get_safe("fPIC", True))),
            "--enable-hardware-specific-code=%s" % yes_no(self.options.hardware_specific_code),
            "--enable-sse2=%s" % yes_no(self.options.sse2),
            "--enable-sse3=%s" % yes_no(self.options.sse3),
            "--enable-ssse3=%s" % yes_no(self.options.ssse3),
            "--enable-sse41=%s" % yes_no(self.options.sse41),
            "--enable-pclmul=%s" % yes_no(self.options.pclmul),
            "--enable-fft-interface=%s" % yes_no(self.options.fft_interface)
        ]
        autotools.configure(args=configure_args, configure_dir=self._source_subfolder)

        return autotools

    @contextlib.contextmanager
    def _build_context(self):
        copy(self, shutil.which("libtool"), src="/", dst=self.build_folder)

        if is_msvc(self):
            with tools.vcvars(self):
                yasm_machine = {
                    "x86": "x86",
                    "x86_64": "amd64",
                }[str(self.settings.arch)]
                env = {
                    "CC": "cl -nologo",
                    "CCAS": "{} -a x86 -m {} -p gas -r raw -f win32 -g null -X gnu".format(os.path.join(self.build_folder, "yasm_wrapper.sh").replace("\\", "/"), yasm_machine),
                    "CXX": "cl -nologo",
                    "AR": "{} lib".format(os.environ["AUTOMAKE"]),
                    "LD": "link -nologo",
                    "NM": "python {}".format(tools.unix_path(os.path.join(self.build_folder, "dumpbin_nm.py"))),
                }

                with tools.environment_append(env):
                    yield
        elif self.settings.compiler in ("clang", "apple-clang"):
            
            compiler_defaults = {
                "CC": "clang",
                "CXX": "clang++",
                "AR": "ar",
                "LD": "clang++",
                "LIBTOOL": shutil.which("libtool")
            }

            env = {}
            for k in ("CC", "CXX", "AR", "LD"):
                v = tools.get_env(k, compiler_defaults.get(k, None))
                if v:
                    env[k] = v
                    
            with tools.environment_append(env):
                yield
        else:
            yield

    def build(self):
        with self._build_context():
            autotools = self._configure_autotools()
            autotools.make()

    def package(self):
        copy(self, "COPYING*", src=self._source_subfolder, dst=os.path.join(self.package_folder, "licenses"))
        with self._build_context():
            autotools = self._configure_autotools()
            autotools.install()

        tools.remove_files_by_mask(os.path.join(self.package_folder, "lib"), "*.la")
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

        if self.options.shared:
            tools.remove_files_by_mask(os.path.join(self.package_folder, "lib"), "*.a")
        else:
            tools.remove_files_by_mask(os.path.join(self.package_folder, "lib"), "*.so")
            tools.remove_files_by_mask(os.path.join(self.package_folder, "lib"), "*.so.*")

        # rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "Gf2x")
        # TODO: Remove in Conan 2.0
        self.cpp_info.names["cmake_find_package"] = "Gf2x"
        self.cpp_info.names["cmake_find_package_multi"] = "Gf2x"

        
        self.cpp_info.components["Gf2x"].names["cmake_find_package"] = "gf2x"
        self.cpp_info.components["Gf2x"].names["cmake_find_package_multi"] = "gf2x"
        self.cpp_info.components["Gf2x"].set_property("cmake_target_name", "Gf2x::gf2x")
        self.cpp_info.components["Gf2x"].set_property("pkg_config_name", "gf2x")
        self.cpp_info.components["Gf2x"].libs = ["gf2x"]


