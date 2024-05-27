import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.build import cross_building
from conan.tools.env import VirtualBuildEnv, VirtualRunEnv, Environment
from conan.tools.files import chdir, copy, get, rm, replace_in_file
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc, VCVars

required_conan_version = ">=1.60.0 <2.0 || >=2.0.6"


class NSSConan(ConanFile):
    name = "nss"
    license = "MPL-2.0"
    homepage = "https://developer.mozilla.org/en-US/docs/Mozilla/Projects/NSS"
    url = "https://github.com/conan-io/conan-center-index"
    description = "Network Security Services"
    topics = ("network", "security", "crypto", "ssl")

    package_type = "shared-library"
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

    def configure(self):
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")
        self.options["nspr"].shared = True
        self.options["sqlite3"].shared = True

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("nspr/4.35", transitive_headers=True, transitive_libs=True)
        self.requires("sqlite3/3.45.2", run=True)
        self.requires("zlib/[>=1.2.11 <2]")

    def validate(self):
        if not self.dependencies["nspr"].options.shared:
            raise ConanInvalidConfiguration("NSS cannot link to static NSPR. Please use option nspr:shared=True")
        if not self.dependencies["sqlite3"].options.shared:
            raise ConanInvalidConfiguration("NSS cannot link to static sqlite. Please use option sqlite3:shared=True")

    def build_requirements(self):
        if self._settings_build.os == "Windows":
            self.win_bash = True
            if not self.conf.get("tools.microsoft.bash:path", check_type=str):
                self.tool_requires("msys2/cci.latest")
        if self.settings.os == "Windows":
            self.tool_requires("mozilla-build/4.0.2")
        if cross_building(self):
            self.tool_requires("sqlite3/<host_version>")
        self.tool_requires("cpython/3.10.0")
        self.tool_requires("ninja/1.11.1")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    @property
    def _site_packages_dir(self):
        return os.path.join(self.build_folder, "site-packages")

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()
        if not cross_building(self):
            env = VirtualRunEnv(self)
            env.generate(scope="build")
        vc = VCVars(self)
        vc.generate()

        # add PYTHONPATH for gyp-next
        env = Environment()
        env.prepend_path("PYTHONPATH", self._site_packages_dir)
        env.prepend_path("PATH", os.path.join(self._site_packages_dir, "bin"))
        env.vars(self, scope="build").save_script("conan_site_packages")

    def _patch_sources(self):
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

        sqlite_info = self.dependencies["sqlite3"].cpp_info.aggregated_components()
        sqlite_flags = " ".join([f"-I{sqlite_info.includedir}"] +
                                _format_libraries(sqlite_info.libs) +
                                _format_library_paths(sqlite_info.libdirs))
        replace_in_file(self, os.path.join(self.source_folder, "nss", "lib", "sqlite", "sqlite.gyp"),
                        "'libraries': ['<(sqlite_libs)'],",
                        f"'libraries': ['{sqlite_flags}'],")

        zlib_info = self.dependencies["zlib"].cpp_info.aggregated_components()
        zlib_flags = " ".join([f"-I{zlib_info.includedir}"] +
                                _format_libraries(zlib_info.libs) +
                                _format_library_paths(zlib_info.libdirs))
        replace_in_file(self, os.path.join(self.source_folder, "nss", "lib", "zlib", "zlib.gyp"),
                        "'libraries': ['<@(zlib_libs)'],",
                        f"'libraries': ['{zlib_flags}'],")

    @property
    def _build_args(self):
        # https://github.com/nss-dev/nss/blob/master/help.txt
        args = []
        # if self.settings.compiler == "gcc":
        #     args.append("XCFLAGS=-Wno-array-parameter")
        args.append("--disable-tests")
        if self.settings.build_type != "Debug":
            args.append("--opt")
        if self.settings.arch == "x86_64":
            args.append("--target=x64")
        elif self.settings.arch == "x86":
            args.append("--target=ia32")
        elif self.settings.arch in ["armv8", "armv8.3"]:
            args.append("--target=aarch64")
        if is_msvc(self):
            args.append("--msvc")
        if not self.options.get_safe("shared", True):
            args.append("--static")
        nspr_root = self.dependencies["nspr"].package_folder
        nspr_includedir = os.path.join(nspr_root, "include", "nspr").replace("\\", "/")
        nspr_libdir = os.path.join(nspr_root, "lib").replace("\\", "/")
        args.append(f"--with-nspr={nspr_includedir}:{nspr_libdir}")
        args.append("--system-sqlite")
        args.append("--enable-legacy-db")  # for libnssdbm3
        return args

    def build(self):
        self._patch_sources()
        # install gyp-next
        self.run(f"python -m pip install gyp-next --no-cache-dir --target={self._site_packages_dir}")
        self.run("gyp --version")

        with chdir(self, os.path.join(self.source_folder, "nss")):
            self.run(f"./build.sh {' '.join(self._build_args)}")

    def package(self):
        copy(self, "COPYING", src=os.path.join(self.source_folder, "nss"), dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "*",
             src=os.path.join(self.source_folder, "dist", "public"),
             dst=os.path.join(self.package_folder, "include"))
        dist_dir = os.path.join(self.source_folder, "dist", "Debug" if self.settings.build_type == "Debug" else "Release")
        copy(self, "*", os.path.join(dist_dir, "bin"), os.path.join(self.package_folder, "bin"))
        for pattern in ["*.a", "*.lib", "*.so", "*.dylib"]:
            copy(self, pattern, os.path.join(dist_dir, "lib"), os.path.join(self.package_folder, "lib"))
        copy(self, "*.dll", os.path.join(dist_dir, "lib"), os.path.join(self.package_folder, "bin"))
        if not self.options.get_safe("shared", True):
            rm(self, "*.so", os.path.join(self.package_folder, "lib"))
            rm(self, "*.dll", os.path.join(self.package_folder, "bin"))
        else:
            rm(self, "*.a", os.path.join(self.package_folder, "lib"))
        fix_apple_shared_install_name(self)

    def package_info(self):
        # Since the project does not export any .pc files,
        # we will rely on the .pc files created by Fedora
        # https://src.fedoraproject.org/rpms/nss/tree/rawhide
        # and Debian
        # https://salsa.debian.org/mozilla-team/nss/-/tree/master/debian
        # instead.

        self.cpp_info.set_property("pkg_config_name", "_nss")

        # https://src.fedoraproject.org/rpms/nss/blob/rawhide/f/nss-util.pc.in
        self.cpp_info.components["nssutil"].set_property("pkg_config_name", "nss-util")
        self.cpp_info.components["nssutil"].libs = ["nssutil3"]
        self.cpp_info.components["nssutil"].includedirs.append(os.path.join("include", "nss"))
        self.cpp_info.components["nssutil"].requires = ["nspr::nspr"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["nssutil"].system_libs = ["pthread", "dl"]

        # https://src.fedoraproject.org/rpms/nss/blob/rawhide/f/nss.pc.in
        self.cpp_info.components["libnss"].set_property("pkg_config_name", "nss")
        self.cpp_info.components["libnss"].libs = ["ssl3", "smime3", "nss3"]
        self.cpp_info.components["libnss"].includedirs.append(os.path.join("include", "nss"))
        self.cpp_info.components["libnss"].requires = ["nspr::nspr", "nssutil"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["libnss"].system_libs = ["pthread", "dl"]

        # https://src.fedoraproject.org/rpms/nss/blob/rawhide/f/nss-softokn.pc.in
        self.cpp_info.components["softokn"].set_property("pkg_config_name", "nss-softokn")
        self.cpp_info.components["softokn"].libs = ["freebl3", "nssdbm3", "softokn3"]
        self.cpp_info.components["softokn"].includedirs.append(os.path.join("include", "nss"))
        self.cpp_info.components["softokn"].requires = ["nspr::nspr", "sqlite3::sqlite3", "nssutil"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["softokn"].system_libs = ["pthread", "dl"]

        self.cpp_info.components["nss_executables"].requires = ["zlib::zlib", "nspr::nspr", "sqlite3::sqlite3"]
