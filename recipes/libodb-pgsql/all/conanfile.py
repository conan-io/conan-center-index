import glob
import os
import shutil
import stat

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import build_jobs, check_min_cppstd
from conan.tools.files import copy, get, rm
from conan.tools.layout import basic_layout

required_conan_version = ">=2.0.9"


class LibOdbPgsqlConan(ConanFile):
    name = "libodb-pgsql"
    description = (
        "PostgreSQL database runtime library for the ODB C++ ORM. "
        "Provides the backend needed to persist C++ objects to a PostgreSQL database."
    )
    license = "GPL-2.0-only"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.codesynthesis.com/products/odb/"
    topics = ("odb", "orm", "postgresql", "pgsql", "database", "c++")
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

    _b2_src = "build2-toolchain-src"
    _pgsql_src = "libodb-pgsql-src"
    _b_bin = "b-bin"

    def layout(self):
        basic_layout(self, src_folder="src")

    def configure(self):
        self.options["libodb"].shared = self.options.shared
        self.options["libpq"].shared = self.options.shared

    def requirements(self):
        self.requires("libodb/2.5.0", transitive_headers=True, transitive_libs=True)
        self.requires("libpq/[>=14 <17]", transitive_headers=True, transitive_libs=True)

    def validate(self):
        if str(self.settings.os) not in ("Windows", "Linux", "Macos"):
            raise ConanInvalidConfiguration(
                f"{self.ref} supports only Windows, Linux and macOS"
            )
        if str(self.settings.arch) not in ("x86_64", "armv8"):
            raise ConanInvalidConfiguration(
                f"{self.ref} supports only x86_64 and armv8"
            )
        if self.settings.get_safe("compiler.cppstd"):
            check_min_cppstd(self, 11)

    def source(self):
        src_data = self.conan_data["sources"][self.version]

        get(
            self,
            **src_data["libodb_pgsql"],
            strip_root=True,
            destination=self._pgsql_source_dir,
        )
        get(
            self,
            **src_data["build2_toolchain"],
            strip_root=True,
            destination=self._build2_source_dir,
        )

    @property
    def _build2_source_dir(self):
        return os.path.join(self.source_folder, self._b2_src)

    @property
    def _pgsql_source_dir(self):
        return os.path.join(self.source_folder, self._pgsql_src)

    def _exe_suffix(self):
        return ".exe" if str(self.settings.os) == "Windows" else ""

    def _b_exe(self):
        return os.path.join(self.source_folder, self._b_bin, "bin", f"b{self._exe_suffix()}")

    def _cxx_exe(self):
        compiler = str(self.settings.compiler)
        version = str(self.settings.compiler.version)
        os_ = str(self.settings.os)

        if compiler == "msvc":
            return "cl"
        if compiler == "gcc":
            return "g++" if os_ == "Windows" else f"g++-{version}"
        if compiler == "clang":
            return f"clang++-{version}"
        if compiler == "apple-clang":
            return "clang++"
        return "c++"

    def _is_msvc(self):
        return str(self.settings.compiler) == "msvc"

    @staticmethod
    def _find_first_existing(candidates):
        for path in candidates:
            if os.path.isfile(path):
                return path
        return None

    def _make_executable(self, path):
        if str(self.settings.os) != "Windows":
            os.chmod(path, os.stat(path).st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)

    def _bootstrap_build2(self):
        b2_pkg = os.path.join(self._build2_source_dir, "build2")
        exe_sfx = self._exe_suffix()
        cxx = self._cxx_exe()

        if self._is_msvc():
            self.run(f"bootstrap-msvc.bat {cxx} /w", cwd=b2_pkg)
        else:
            bootstrap = os.path.join(b2_pkg, "bootstrap.sh")
            self._make_executable(bootstrap)
            self.run(f"./bootstrap.sh {cxx} -w", cwd=b2_pkg)

        old_boot = os.path.join(b2_pkg, "build2", f"b-boot{exe_sfx}")
        new_boot = os.path.join(b2_pkg, "b", f"b-boot{exe_sfx}")
        b_boot = self._find_first_existing([old_boot, new_boot])

        if not b_boot:
            raise ConanInvalidConfiguration(
                f"Could not find build2 bootstrap executable after phase 1 in {b2_pkg}"
            )

        if b_boot == new_boot:
            b_target = "b/exe{b}"
            b_full_candidates = [os.path.join(b2_pkg, "b", f"b{exe_sfx}")]
        else:
            b_target = "build2/exe{b}"
            b_full_candidates = [os.path.join(b2_pkg, "build2", f"b{exe_sfx}")]

        self.output.info(f"Using build2 bootstrap executable: {b_boot}")
        self.output.info(f"Using build2 rebuild target: {b_target}")

        self.run(
            f'"{b_boot}" config.cxx={cxx} config.bin.lib=static {b_target}',
            cwd=b2_pkg,
        )

        b_full = self._find_first_existing(b_full_candidates)
        if not b_full:
            raise ConanInvalidConfiguration(
                f"Could not find final build2 executable after phase 2 in {b2_pkg}"
            )

        self.output.info(f"Using final build2 executable: {b_full}")

        b_bin_dir = os.path.join(self.source_folder, self._b_bin, "bin")
        os.makedirs(b_bin_dir, exist_ok=True)

        b_final = os.path.join(b_bin_dir, f"b{exe_sfx}")
        shutil.copy2(b_full, b_final)
        self._make_executable(b_final)

    def _dep_info(self, name):
        return self.dependencies[name].cpp_info.aggregated_components()

    def _dep_include_dir(self, name):
        return self._dep_info(name).includedirs[0].replace("\\", "/")

    def _dep_lib_dir(self, name):
        return self._dep_info(name).libdirs[0].replace("\\", "/")

    def _cc_flag(self, kind, value):
        if self._is_msvc():
            flag = f"/I{value}" if kind == "include" else f"/LIBPATH:{value}"
        else:
            flag = f"-I{value}" if kind == "include" else f"-L{value}"

        key = "config.cc.poptions" if kind == "include" else "config.cc.loptions"
        return f"{key}+={flag}"

    def _stage_shared_dep_libs(self, name):
        info = self._dep_info(name)
        stage_dir = os.path.join(self.build_folder, "dep-link", name)
        os.makedirs(stage_dir, exist_ok=True)

        wanted = [lib.lower() for lib in info.libs]
        os_ = str(self.settings.os)
        if os_ == "Windows":
            patterns = ("*.dll.lib", "*.lib")
        elif os_ == "Macos":
            patterns = ("*.dylib",)
        else:
            patterns = ("*.so", "*.so.*")

        copied = []
        for libdir in info.libdirs:
            for pattern in patterns:
                for src in glob.glob(os.path.join(libdir, pattern)):
                    basename = os.path.basename(src).lower()
                    if wanted and not any(lib in basename for lib in wanted):
                        continue
                    dst = os.path.join(stage_dir, os.path.basename(src))
                    shutil.copy2(src, dst)
                    copied.append(dst)

        if not copied:
            raise ConanInvalidConfiguration(
                f"Could not find shared library artifacts for dependency '{name}'"
            )

        return stage_dir.replace("\\", "/")

    def _link_libdir(self, name):
        if self.options.shared and str(self.settings.os) in ("Windows", "Macos"):
            return self._stage_shared_dep_libs(name)
        return self._dep_lib_dir(name)

    def _build_args(self):
        args = []
        debug = str(self.settings.build_type) in ("Debug", "RelWithDebInfo")
        jobs = build_jobs(self)

        if jobs > 1:
            args.append(f"-j {jobs}")

        args.extend([
            f"config.cxx={self._cxx_exe()}",
            "config.cxx.std=c++11",
            f"config.bin.debug={'true' if debug else 'false'}",
            f"config.bin.lib={'shared' if self.options.shared else 'static'}",
            self._cc_flag("include", self._dep_include_dir("libodb")),
            self._cc_flag("include", self._dep_include_dir("libpq")),
            self._cc_flag("libpath", self._link_libdir("libodb")),
            self._cc_flag("libpath", self._link_libdir("libpq")),
            "config.libodb_pgsql.develop=false",
        ])

        if self.options.shared and str(self.settings.os) != "Windows":
            args.append(f"config.bin.rpath={self.package_folder}/lib")

        if not self.options.shared and self.options.get_safe("fPIC") and not self._is_msvc():
            args.append("config.cc.coptions+=-fPIC")

        return args

    def build(self):
        self._bootstrap_build2()
        args = " ".join(self._build_args())
        self.run(f'"{self._b_exe()}" {args} ./odb/pgsql/', cwd=self._pgsql_source_dir)

    def _copy_headers(self):
        src = os.path.join(self._pgsql_source_dir, "odb", "pgsql")
        dst = os.path.join(self.package_folder, "include", "odb", "pgsql")
        for pattern in ("*.hxx", "*.ixx", "*.txx", "*.h"):
            copy(self, pattern, src, dst)

    def _copy_libraries(self):
        lib_dir = os.path.join(self.package_folder, "lib")
        bin_dir = os.path.join(self.package_folder, "bin")

        if self.options.shared:
            copy(self, "*.dll", self._pgsql_source_dir, bin_dir, keep_path=False)
            copy(self, "*.so*", self._pgsql_source_dir, lib_dir, keep_path=False)
            copy(self, "*.dylib", self._pgsql_source_dir, lib_dir, keep_path=False)
            copy(self, "*.lib", self._pgsql_source_dir, lib_dir, keep_path=False)
        else:
            copy(self, "*.a", self._pgsql_source_dir, lib_dir, keep_path=False)
            copy(self, "*.lib", self._pgsql_source_dir, lib_dir, keep_path=False)

    def package(self):
        self._copy_headers()
        self._copy_libraries()

        copy(
            self,
            "LICENSE",
            self._pgsql_source_dir,
            os.path.join(self.package_folder, "licenses"),
            keep_path=False,
        )
        rm(self, "*.pdb", self.package_folder, recursive=True)

    def package_info(self):
        self.cpp_info.libs = ["odb-pgsql"]
        self.cpp_info.set_property("cmake_file_name", "libodb-pgsql")
        self.cpp_info.set_property("cmake_target_name", "libodb-pgsql::libodb-pgsql")
        self.cpp_info.set_property("pkg_config_name", "libodb-pgsql")
        self.cpp_info.requires = ["libodb::libodb", "libpq::pq"]

        if not self.options.shared:
            self.cpp_info.defines.append("LIBODB_PGSQL_STATIC")

        if str(self.settings.os) == "Linux":
            self.cpp_info.system_libs.append("pthread")
        elif str(self.settings.os) == "Windows":
            self.cpp_info.system_libs.append("ws2_32")