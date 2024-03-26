from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import fix_apple_shared_install_name, is_apple_os
from conan.tools.build import cross_building
from conan.tools.env import VirtualBuildEnv, VirtualRunEnv
from conan.tools.files import chdir, copy, get, rename, rm
from conan.tools.gnu import AutotoolsToolchain, Autotools
from conan.tools.microsoft import is_msvc, msvc_runtime_flag, VCVars
import os
import glob

required_conan_version = ">=1.60.0 <2.0 || >=2.0.6"


class NSSConan(ConanFile):
    name = "nss"
    license = "MPL-2.0"
    homepage = "https://developer.mozilla.org/en-US/docs/Mozilla/Projects/NSS"
    url = "https://github.com/conan-io/conan-center-index"
    description = "Network Security Services"
    topics = ("network", "security", "crypto", "ssl")

    package_type = "static-library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "fPIC": [True, False],
    }
    default_options = {
        "fPIC": True,
    }

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")
        self.options["nspr"].shared = True
        self.options["sqlite3"].shared = True

    def requirements(self):
        self.requires("nspr/4.35", transitive_headers=True, transitive_libs=True)
        self.requires("sqlite3/3.45.2", run=True)
        self.requires("zlib/[>=1.2.11 <2]")

    def validate(self):
        if msvc_runtime_flag(self) == "MTd":
            raise ConanInvalidConfiguration("NSS recipes does not support MTd runtime. Contributions are welcome.")
        if not self.dependencies["nspr"].options.shared:
            raise ConanInvalidConfiguration("NSS cannot link to static NSPR. Please use option nspr:shared=True")
        if not self.dependencies["sqlite3"].options.shared:
            raise ConanInvalidConfiguration("NSS cannot link to static sqlite. Please use option sqlite3:shared=True")
        if self.settings.arch in ["armv8", "armv8.3"] and is_apple_os(self):
            raise ConanInvalidConfiguration("Macos ARM64 builds not yet supported. Contributions are welcome.")

    def build_requirements(self):
        if self._settings_build.os == "Windows":
            self.win_bash = True
            if not self.conf.get("tools.microsoft.bash:path", check_type=str):
                self.tool_requires("msys2/cci.latest")
        if self.settings.os == "Windows":
            self.tool_requires("mozilla-build/4.0.2")
        if cross_building(self):
            self.tool_requires("sqlite3/<host_version>")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()
        if not cross_building(self):
            env = VirtualRunEnv(self)
            env.generate(scope="build")
        vc = VCVars(self)
        vc.generate()

        def adjust_path(path):
            """
            adjusts path to be safely passed to the compiler command line
            for Windows bash, ensures path is in format according to the subsystem
            for path with spaces, places double quotes around it
            converts slashes to backslashes, or vice versa
            """
            if is_msvc(self):
                path = path.replace('/', '\\')
            else:
                path = path.replace('\\', '/')
            return f'"{path}"' if ' ' in path else path

        def _format_library_paths(library_paths):
            pattern = "-LIBPATH:%s" if is_msvc(self) else "-L%s"
            return [pattern % adjust_path(library_path)
                    for library_path in library_paths if library_path]

        def _format_libraries(libraries):
            result = []
            for library in libraries:
                if is_msvc(self):
                    if not library.endswith(".lib"):
                        library += ".lib"
                    result.append(library)
                else:
                    result.append(f"-l{library}")
            return result

        tc = AutotoolsToolchain(self)
        args = []
        if self.settings.arch in ["x86_64"]:
            args.append("USE_64=1")
            if self.settings.os == "Macos":
                args.append("CPU_ARCH=i386")
            else:
                args.append("CPU_ARCH=x86_64")
        elif self.settings.arch in ["armv8", "armv8.3"]:
            args.append("USE_64=1")
            args.append("CPU_ARCH=aarch64")

        if cross_building(self):
            args.append("CROSS_COMPILE=1")

        if self.settings.compiler == "gcc":
            args.append("XCFLAGS=-Wno-array-parameter")

        nspr_root = self.dependencies["nspr"].package_folder
        args.append(f"NSPR_INCLUDE_DIR={adjust_path(os.path.join(nspr_root, 'include', 'nspr'))}")
        args.append(f"NSPR_LIB_DIR={adjust_path(os.path.join(nspr_root, 'lib'))}")
        if is_msvc(self):
            args.append("NSPR31_LIB_PREFIX=$(NULL)")

        os_id = {
            "Linux": "Linux",
            "Macos": "Darwin",
            "Windows": "WINNT",
            "FreeBSD": "FreeBSD",
        }.get(str(self.settings.os), "UNSUPPORTED_OS")
        args.append(f"OS_TARGET={os_id}")
        args.append(f"OS_ARCH={os_id}")

        if self.settings.build_type != "Debug":
            args.append("BUILD_OPT=1")

        args.append("USE_SYSTEM_ZLIB=1")
        zlib_cpp_info = self.dependencies["zlib"].cpp_info.aggregated_components()
        args.append(f"ZLIB_INCLUDE_DIR={zlib_cpp_info.includedir}")
        args.append("ZLIB_LIBS=%s" % " ".join(
            _format_libraries(zlib_cpp_info.libs) +
            _format_library_paths(zlib_cpp_info.libdirs)
        ))

        args.append("NSS_DISABLE_GTESTS=1")

        args.append("NSS_USE_SYSTEM_SQLITE=1")
        sqlite3_cpp_info = self.dependencies["sqlite3"].cpp_info.aggregated_components()
        args.append(f"SQLITE_INCLUDE_DIR={sqlite3_cpp_info.includedir}")
        args.append(f"SQLITE_LIB_DIR={sqlite3_cpp_info.libdir}")

        args.append("NSDISTMODE=copy")

        tc.make_args += args
        tc.generate()


    def build(self):
        with chdir(self, os.path.join(self.source_folder, "nss")):
            autotools = Autotools(self)
            autotools.make()

    def package(self):
        copy(self, "COPYING", src=os.path.join(self.source_folder, "nss"), dst=os.path.join(self.package_folder, "licenses"))
        with chdir(self, os.path.join(self.source_folder, "nss")):
            autotools = Autotools(self)
            autotools.install()
        copy(self, "*",
                  src=os.path.join(self.source_folder, "dist", "public", "nss"),
                  dst=os.path.join(self.package_folder, "include"))
        for d in os.listdir(os.path.join(self.source_folder, "dist")):
            if d in ["private", "public"]:
                continue
            f = os.path.join(self.source_folder, "dist", d)
            if not os.path.isdir(f):
                continue
            copy(self, "*", src=f, dst=self.package_folder)

        for dll_file in glob.glob(os.path.join(self.package_folder, "lib", "*.dll")):
            rename(self, dll_file, os.path.join(self.package_folder, "bin", os.path.basename(dll_file)))

        rm(self, "*.so", os.path.join(self.package_folder, "lib"))
        rm(self, "*.dll", os.path.join(self.package_folder, "bin"))
        fix_apple_shared_install_name(self)

    def package_info(self):
        def _library_name(lib,vers):
            # return f"{lib}{vers}" if self.options.shared else lib
            return lib
        self.cpp_info.components["libnss"].libs.append(_library_name("nss", 3))
        self.cpp_info.components["libnss"].requires = ["nssutil", "nspr::nspr"]

        self.cpp_info.components["nssutil"].libs = [_library_name("nssutil", 3)]
        self.cpp_info.components["nssutil"].requires = ["nspr::nspr"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["nssutil"].system_libs = ["pthread"]

        self.cpp_info.components["softokn"].libs = [_library_name("softokn", 3)]
        self.cpp_info.components["softokn"].requires = ["sqlite3::sqlite3", "nssutil", "nspr::nspr"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["softokn"].system_libs = ["pthread"]

        self.cpp_info.components["nssdbm"].libs = [_library_name("nssdbm", 3)]
        self.cpp_info.components["nssdbm"].requires = ["nspr::nspr", "nssutil"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["nssdbm"].system_libs = ["pthread"]

        self.cpp_info.components["smime"].libs = [_library_name("smime", 3)]
        self.cpp_info.components["smime"].requires = ["nspr::nspr", "libnss", "nssutil"]

        self.cpp_info.components["ssl"].libs = [_library_name("ssl", 3)]
        self.cpp_info.components["ssl"].requires = ["nspr::nspr", "libnss", "nssutil"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["ssl"].system_libs = ["pthread"]

        self.cpp_info.components["nss_executables"].requires = ["zlib::zlib"]

        self.cpp_info.set_property("pkg_config_name", "nss")
