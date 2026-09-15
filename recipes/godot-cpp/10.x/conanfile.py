import glob
import os
import re
import shutil
import subprocess

from conan import ConanFile
from conan.errors import ConanException, ConanInvalidConfiguration
from conan.tools.apple import is_apple_os
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import copy, get
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version

required_conan_version = ">=2.0.0"


class GodotCppConan(ConanFile):
    name = "godot-cpp"
    description = "C++ bindings for the Godot Engine's GDExtensions API"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/godotengine/godot-cpp"
    topics = ("godot", "game-engine", "gdextension", "bindings")
    package_type = "static-library"
    settings = "os", "arch", "compiler", "build_type"

    options = {
        "api_version": ["4.3", "4.4", "4.5", "4.6", "4.7"],
        "target": ["template_debug", "template_release", "editor"],
        "precision": ["single", "double"],
        "hot_reload_enabled": [True, False],
    }
    default_options = {
        "api_version": "4.7",
        "target": "template_debug",
        "precision": "single",
        "hot_reload_enabled": False,
    }

    # API JSONs bundled per release (gdextension/extension_api-<X-Y>.json)
    _latest_api_version = {
        "10.0.0-rc1": "4.6",
        "10.0.0-rc2": "4.7",
    }

    # Emscripten versions used by Godot's official web builds, per API version
    # (source: EM_VERSION in .github/workflows/web_builds.yml on each
    # godotengine/godot tag). GDExtension side modules must be built with the
    # same Emscripten version as the engine's web template.
    _emsdk_version = {
        "4.3": "3.1.64",
        "4.4": "3.1.64",
        "4.5": "4.0.11",
        "4.6": "4.0.11",
        "4.7": "4.0.11",
    }

    def layout(self):
        cmake_layout(self, src_folder="src")

    def build_requirements(self):
        self.tool_requires("cmake/3.31.12")
        # NOTE: upstream's CMake runs find_package(Python3 COMPONENTS Interpreter REQUIRED)
        # to generate the bindings at configure/build time; a system Python >= 3.4
        # must be available on PATH.

    def config_options(self):
        if self.version in self._latest_api_version:
            self.options.api_version = self._latest_api_version[self.version]

    def validate(self):
        if self.settings.os not in ("Windows", "Linux", "Macos", "iOS", "Android", "Emscripten"):
            raise ConanInvalidConfiguration(f"{self.ref} does not support {self.settings.os}")
        if self.settings.os == "Emscripten" and self.settings.arch != "wasm":
            raise ConanInvalidConfiguration(f"{self.ref} on Emscripten requires arch=wasm")
        if self.settings.os == "Android" and Version(str(self.settings.os.api_level)) < "24":
            raise ConanInvalidConfiguration(f"{self.ref} on Android requires os.api_level >= 24 (upstream minimum)")
        latest = self._latest_api_version.get(self.version, "4.7")
        if Version(str(self.options.api_version)) > Version(latest):
            raise ConanInvalidConfiguration(
                f"godot-cpp {self.version} does not bundle the Godot {self.options.api_version} "
                f"extension API (latest available is {latest})"
            )

        if self.settings.compiler.get_safe("cppstd"):
            # Profiles without compiler.cppstd are allowed through (no way to
            # check); check_min_cppstd would otherwise reject them.
            check_min_cppstd(self, 17)
        minimum_compiler_version = {
            "gcc": 8,
            "clang": 7,
            "apple-clang": 12,
            "msvc": 192,
        }
        compiler = str(self.settings.compiler)
        if compiler not in minimum_compiler_version:
            self.output.warning(f"Unknown compiler {compiler}, assuming C++17 support.")
        elif Version(self.settings.compiler.version) < minimum_compiler_version[compiler]:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++17; {compiler} "
                f"{minimum_compiler_version[compiler]} or newer is required."
            )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        VirtualBuildEnv(self).generate()
        tc = CMakeToolchain(self)
        tc.cache_variables["GODOTCPP_API_VERSION"] = str(self.options.api_version)
        tc.cache_variables["GODOTCPP_TARGET"] = str(self.options.target)
        tc.cache_variables["GODOTCPP_PRECISION"] = str(self.options.precision)
        # Pin hot reload explicitly: left empty, 10.0.0-rc1 enables it automatically
        # whenever target != template_release (inherits DEBUG_FEATURES), diverging
        # from rc2 and from the defines packaged by package_info().
        tc.cache_variables["GODOTCPP_USE_HOT_RELOAD"] = "ON" if self.options.hot_reload_enabled else "OFF"
        tc.generate()

    def _emcc_executable(self):
        emcc = shutil.which("emcc")
        if emcc is None:
            # emsdk root from EMSDK env var (set by emsdk_env) or derived from
            # the user_toolchain conf pointing at Platform/Emscripten.cmake
            roots = [os.environ.get("EMSDK")]
            user_toolchain = self.conf.get("tools.cmake.cmaketoolchain:user_toolchain", check_type=list)
            for toolchain in user_toolchain or []:
                if "Platform/Emscripten.cmake" in toolchain.replace("\\", "/"):
                    # <root>/upstream/emscripten/cmake/Modules/Platform/Emscripten.cmake
                    roots.append(os.path.abspath(os.path.join(toolchain, "..", "..", "..", "..", "..", "..")))
            for root in roots:
                if root and os.path.isdir(root):
                    names = ("emcc.exe", "emcc.bat") if self.settings_build.os == "Windows" else ("emcc",)
                    for name in names:
                        candidate = os.path.join(root, "upstream", "emscripten", name)
                        if os.path.isfile(candidate):
                            emcc = candidate
                            break
                if emcc:
                    break
        return emcc

    def _validate_emscripten_version(self):
        emcc = self._emcc_executable()
        if emcc is None:
            raise ConanException(
                "emcc not found: activate the Emscripten SDK (emsdk_env / EMSDK env var) "
                "or point tools.cmake.cmaketoolchain:user_toolchain at the emsdk "
                "Platform/Emscripten.cmake in the profile"
            )
        output = subprocess.check_output([emcc, "--version"], text=True).splitlines()[0]
        match = re.search(r"emcc\s+\(.*\)\s+(\d+\.\d+\.\d+)", output)
        found = match.group(1) if match else "unknown"
        required = self._emsdk_version.get(str(self.options.api_version))
        if required is not None and found != required:
            raise ConanException(
                f"Emscripten {required} is required for api_version={self.options.api_version} "
                f"(version used by Godot's official web builds), but emcc reports {found}. "
                f"Install it with: emsdk install {required} && emsdk activate {required}"
            )

    def build(self):
        if self.settings.os == "Emscripten":
            self._validate_emscripten_version()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE.md", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        # Upstream provides no install()/export rules; package the static headers,
        # the generated headers and the static library manually. The include trees
        # merge without collisions (static: include/godot_cpp/{core,templates,...},
        # generated: gdextension_interface.h + gen include/godot_cpp/{classes,variant,...}).
        copy(self, "*", src=os.path.join(self.source_folder, "include"),
             dst=os.path.join(self.package_folder, "include"))
        copy(self, "*", src=os.path.join(self.build_folder, "gen", "include"),
             dst=os.path.join(self.package_folder, "include"))
        # bin/libgodot-cpp.<platform>.<target>[...].<arch>.{a,lib} -> canonical name
        built_libs = glob.glob(os.path.join(self.build_folder, "bin", "libgodot-cpp.*"))
        if len(built_libs) != 1:
            raise ConanException(f"expected exactly one built godot-cpp library, found {built_libs}")
        lib_dst = os.path.join(self.package_folder, "lib")
        os.makedirs(lib_dst, exist_ok=True)
        if is_msvc(self):
            shutil.copy(built_libs[0], os.path.join(lib_dst, "godot-cpp.lib"))
        else:
            shutil.copy(built_libs[0], os.path.join(lib_dst, "libgodot-cpp.a"))

    def package_info(self):
        self.cpp_info.libs = ["godot-cpp"]
        self.cpp_info.includedirs = ["include"]

        # Recreates the PUBLIC definitions of the upstream CMake target, which are
        # lost by the manual packaging (no exported GodotCppConfig.cmake).
        defines = ["GDEXTENSION", "THREADS_ENABLED"]
        if self.settings.os == "Windows":
            defines.append("WINDOWS_ENABLED")
        elif self.settings.os == "Linux":
            defines.extend(["LINUX_ENABLED", "UNIX_ENABLED"])
        elif self.settings.os == "Android":
            defines.extend(["ANDROID_ENABLED", "UNIX_ENABLED"])
        elif self.settings.os == "iOS":
            defines.extend(["IOS_ENABLED", "UNIX_ENABLED"])
        elif self.settings.os == "Emscripten":
            defines.extend(["WEB_ENABLED", "UNIX_ENABLED"])
        elif is_apple_os(self):
            defines.extend(["MACOS_ENABLED", "UNIX_ENABLED"])
        if is_msvc(self):
            defines.extend(["TYPED_METHOD_BIND", "NOMINMAX", "_HAS_EXCEPTIONS=0"])
        if self.options.target != "template_release":
            defines.append("DEBUG_ENABLED")
        if self.options.precision == "double":
            defines.append("REAL_T_IS_DOUBLE")
        if self.options.hot_reload_enabled:
            defines.append("HOT_RELOAD_ENABLED")
        self.cpp_info.defines = defines
        if is_msvc(self):
            self.cpp_info.cxxflags = ["/utf-8"]
        if self.settings.os == "Emscripten":
            # Recreates the PUBLIC compile / INTERFACE link flags of upstream
            # cmake/web.cmake so consumer GDExtensions link as wasm side modules.
            self.cpp_info.cxxflags = ["-sSIDE_MODULE=1", "-sSUPPORT_LONGJMP=wasm", "-sUSE_PTHREADS=1"]
            self.cpp_info.linkflags = ["-sSIDE_MODULE=1", "-sWASM_BIGINT", "-sSUPPORT_LONGJMP=wasm", "-sUSE_PTHREADS=1"]

        self.cpp_info.set_property("pkg_config_name", "godot-cpp")
        self.cpp_info.set_property("cmake_target_name", "godot-cpp::godot-cpp")
        self.cpp_info.set_property("cmake_file_name", "godot-cpp")
