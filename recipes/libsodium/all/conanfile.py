from conan.tools.microsoft import msvc_runtime_flag
from conans import ConanFile, AutoToolsBuildEnvironment, tools, MSBuild
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.43.0"


class LibsodiumConan(ConanFile):
    name = "libsodium"
    description = "A modern and easy-to-use crypto library."
    license = "ISC"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://doc.libsodium.org/"
    topics = ("sodium", "libsodium", "encryption", "signature", "hashing")

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "use_soname": [True, False],
        "PIE": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "use_soname": True,
        "PIE": False,
    }

    short_paths = True

    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    @property
    def _is_msvc(self):
        return str(self.settings.compiler) in ["Visual Studio", "msvc"]

    @property
    def _is_mingw(self):
        return self.settings.os == "Windows" and self.settings.compiler == "gcc"

    def export_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def validate(self):
        if self.options.shared and self._is_msvc and "MT" in msvc_runtime_flag(self):
            raise ConanInvalidConfiguration("Cannot build shared libsodium libraries with static runtime")

    def build_requirements(self):
        if not self._is_msvc:
            if self._is_mingw:
                self.build_requires("libtool/2.4.6")
            if self._settings_build.os == "Windows" and not tools.get_env("CONAN_BASH_PATH"):
                self.build_requires("msys2/cci.latest")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    @property
    def _msvc_sln_folder(self):
        if self.settings.compiler == "Visual Studio":
            folder = {
                "10": "vs2010",
                "11": "vs2012",
                "12": "vs2013",
                "14": "vs2015",
                "15": "vs2017",
                "16": "vs2019",
            }
        else:
            folder = {
                "190": "vs2015",
                "191": "vs2017",
                "192": "vs2019",
            }

        if self.version != "1.0.18":
            if self.settings.compiler == "Visual Studio":
                folder["17"] = "vs2022"
            else:
                folder["193"] = "vs2022"

        return folder.get(str(self.settings.compiler.version))

    def _build_msvc(self):
        msvc_sln_folder = self._msvc_sln_folder or ("vs2022" if self.version != "1.0.18" else "vs2019")
        upgrade_project = self._msvc_sln_folder is None
        sln_path = os.path.join(self.build_folder, self._source_subfolder, "builds", "msvc", msvc_sln_folder, "libsodium.sln")
        build_type = "{}{}".format(
            "Dyn" if self.options.shared else "Static",
            "Debug" if self.settings.build_type == "Debug" else "Release",
        )
        msbuild = MSBuild(self)
        msbuild.build(sln_path, upgrade_project=upgrade_project, platforms={"x86": "Win32"}, build_type=build_type)

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        if self._is_mingw:
            self._autotools.libs.append("ssp")

        if self.settings.os == "Emscripten":
            self.output.warn("os=Emscripten is not tested/supported by this recipe")
            # FIXME: ./dist-build/emscripten.sh does not respect options of this recipe

        yes_no = lambda v: "yes" if v else "no"
        args = [
            "--enable-shared={}".format(yes_no(self.options.shared)),
            "--enable-static={}".format(yes_no(not self.options.shared)),
            "--enable-soname-versions={}".format(yes_no(self.options.use_soname)),
            "--enable-pie={}".format(yes_no(self.options.PIE)),
        ]

        self._autotools.configure(args=args, configure_dir=self._source_subfolder)
        return self._autotools

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        if self._is_msvc:
            self._build_msvc()
        else:
            if self._is_mingw:
                self.run("{} -fiv".format(tools.get_env("AUTORECONF")), cwd=self._source_subfolder, win_bash=tools.os_info.is_windows)
            if tools.is_apple_os(self.settings.os):
                # Relocatable shared lib for Apple platforms
                tools.replace_in_file(
                    os.path.join(self._source_subfolder, "configure"),
                    "-install_name \\$rpath/",
                    "-install_name @rpath/"
                )
            autotools = self._configure_autotools()
            autotools.make()

    def package(self):
        self.copy("*LICENSE", dst="licenses", keep_path=False)
        if self._is_msvc:
            self.copy("*.lib", dst="lib", keep_path=False)
            self.copy("*.dll", dst="bin", keep_path=False)
            inc_src = os.path.join(self._source_subfolder, "src", self.name, "include")
            self.copy("*.h", src=inc_src, dst="include", keep_path=True, excludes=("*/private/*"))
        else:
            autotools = self._configure_autotools()
            autotools.install()
            tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
            tools.remove_files_by_mask(os.path.join(self.package_folder, "lib"), "*.la")

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "libsodium")
        self.cpp_info.libs = ["{}sodium".format("lib" if self._is_msvc else "")]
        if not self.options.shared:
            self.cpp_info.defines = ["SODIUM_STATIC"]
        if self.settings.os in ("FreeBSD", "Linux"):
            self.cpp_info.system_libs.append("pthread")
        if self._is_mingw:
            self.cpp_info.system_libs.append("ssp")
