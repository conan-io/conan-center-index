from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.env import Environment, VirtualBuildEnv, VirtualRunEnv
from conan.tools.files import copy, get, chdir
from conan.tools.build import check_min_cppstd, cross_building
from conan.tools.scm import Version
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc, unix_path
import os


required_conan_version = ">=1.53.0"

class SqlParserConan(ConanFile):
    name = "sql-parser"
    description = "SQL Parser for C++. Building C++ object structure from SQL statements."
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/hyrise/sql-parser/"
    topics = ("sql", "parser", "hyrise")
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

    @property
    def _min_cppstd(self):
        return 17

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "7",
            "clang": "7",
            "apple-clang": "10",
            "Visual Studio": "15",
            "msvc": "191",
        }

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
            self.options.rm_safe("fPIC")

    def layout(self):
        basic_layout(self, src_folder="src")

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )

    def build_requirements(self):
        if self._settings_build.os == "Windows":
            self.win_bash = True
            if not self.conf.get("tools.microsoft.bash:path", default=False, check_type=str):
                self.tool_requires("msys2/cci.latest")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()
        if not cross_building(self):
            env = VirtualRunEnv(self)
            env.generate(scope="build")

        tc: AutotoolsToolchain = AutotoolsToolchain(self)
        if self.settings.build_type == "Debug":
            tc.make_args.append("mode=debug")
        if not self.options.shared:
            tc.make_args.append("static=yes")
        tc.generate()

        if is_msvc(self):
            env = Environment()
            compile_wrapper = unix_path(self, self._user_info_build["automake"].compile)
            ar_wrapper = unix_path(self, self._user_info_build["automake"].ar_lib)
            env.define("CC", f"{compile_wrapper} cl -nologo")
            env.define("CXX", f"{compile_wrapper} cl -nologo")
            env.define("LD", "link -nologo")
            env.define("AR", f"{ar_wrapper} \"lib -nologo\"")
            env.define("NM", "dumpbin -symbols")
            env.define("OBJDUMP", ":")
            env.define("RANLIB", ":")
            env.define("STRIP", ":")
            env.vars(self).save_script("conanbuild_msvc")

    def build(self):
        with chdir(self, self.source_folder):
            autotools = Autotools(self)
            autotools.make()

    def package(self):
        copy(self, pattern="LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))

        copy(self, "*.h", src=os.path.join(self.source_folder, "src"), dst=os.path.join(self.package_folder, "include", "hsql"))
        copy(self, "*.a", src=os.path.join(self.build_folder, os.pardir), dst=os.path.join(self.package_folder, "lib"), keep_path=False)
        copy(self, "*.so", src=os.path.join(self.build_folder, os.pardir), dst=os.path.join(self.package_folder, "lib"), keep_path=False)
        copy(self, "*.dylib", src=os.path.join(self.build_folder, os.pardir), dst=os.path.join(self.package_folder, "lib"), keep_path=False)
        copy(self, "*.lib", src=os.path.join(self.build_folder, os.pardir), dst=os.path.join(self.package_folder, "lib"), keep_path=False)
        copy(self, "*.dll", src=os.path.join(self.build_folder, os.pardir), dst=os.path.join(self.package_folder, "bin"), keep_path=False)

    def package_info(self):
        self.cpp_info.libs = ["sqlparser"]

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["dl", "m", "pthread"])
