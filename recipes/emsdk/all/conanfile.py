from conan import ConanFile
from conan.tools.build import cross_building
from conan.tools.files import chdir, copy, get, replace_in_file
from conan.tools.layout import basic_layout
from conans import tools as tools_legacy
import json
import os

required_conan_version = ">=1.46.0"


class EmSDKConan(ConanFile):
    name = "emsdk"
    description = "Emscripten SDK. Emscripten is an Open Source LLVM to JavaScript compiler"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/kripken/emscripten"
    topics = ("emsdk", "emscripten", "sdk")
    license = "MIT"
    settings = "os", "arch", "compiler", "build_type"

    short_paths = True

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def requirements(self):
        self.requires("nodejs/16.3.0")
        # self.requires("python")  # FIXME: Not available as Conan package
        # self.requires("wasm")  # FIXME: Not available as Conan package

    def package_id(self):
        del self.info.settings.compiler
        del self.info.settings.build_type

    def layout(self):
        basic_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    @staticmethod
    def _chmod_plus_x(filename):
        if os.name == "posix":
            os.chmod(filename, os.stat(filename).st_mode | 0o111)

    def _tools_for_version(self):
        ret = {}
        # Select release-upstream from version (wasm-binaries)
        with open(os.path.join(self.source_folder, "emscripten-releases-tags.json"), "r") as f:
            data = json.load(f)
            ret["wasm"] = f"releases-upstream-{data['releases'][self.version]}-64bit"
        # Select python and node versions
        with open(os.path.join(self.source_folder, "emsdk_manifest.json"), "r") as f:
            data = json.load(f)
            tools = data["tools"]
            if self.settings.os == "Windows":
                python = next((it for it in tools if (it["id"] == "python" and not it.get("is_old", False))), None)
                ret["python"] = f"python-{python['version']}-64bit"
            node = next((it for it in tools if (it["id"] == "node" and not it.get("is_old", False))), None)
            ret["nodejs"] = f"node-{node['version']}-64bit"
        return ret

    def build(self):
        with chdir(self, self.source_folder):
            emsdk = "emsdk.bat" if self._settings_build.os == "Windows" else "./emsdk"
            self._chmod_plus_x("emsdk")

            # Install required tools
            required_tools = self._tools_for_version()
            for key, value in required_tools.items():
                if key != 'nodejs':
                    self.run(f"{emsdk} install {value}")
                    self.run(f"{emsdk} activate {value}")

    @property
    def _emscripten_env(self):
        return {
            "PATH": [
                self.package_folder,
                os.path.join(self.package_folder, "bin", "upstream", "emscripten"),
            ],
            "EMSDK": self.package_folder,
            "EMSCRIPTEN": os.path.join(self.package_folder, "bin", "upstream", "emscripten"),
            "EM_CONFIG": os.path.join(self.package_folder, "bin", ".emscripten"),
            "EM_CACHE": os.path.join(self.package_folder,  "bin", ".emscripten_cache"),
        }

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "*", src=self.source_folder, dst=os.path.join(self.package_folder, "bin"))
        emscripten = os.path.join(self.package_folder, "bin", "upstream", "emscripten")
        toolchain = os.path.join(emscripten, "cmake", "Modules", "Platform", "Emscripten.cmake")
        # FIXME: conan should add the root of conan package requirements to CMAKE_PREFIX_PATH (LIBRARY/INCLUDE -> ONLY; PROGRAM -> NEVER)
        # allow to find conan libraries
        replace_in_file(self, toolchain,
                              "set(CMAKE_FIND_ROOT_PATH_MODE_LIBRARY ONLY)",
                              "set(CMAKE_FIND_ROOT_PATH_MODE_LIBRARY BOTH)")
        replace_in_file(self, toolchain,
                              "set(CMAKE_FIND_ROOT_PATH_MODE_INCLUDE ONLY)",
                              "set(CMAKE_FIND_ROOT_PATH_MODE_INCLUDE BOTH)")
        replace_in_file(self, toolchain,
                              "set(CMAKE_FIND_ROOT_PATH_MODE_PACKAGE ONLY)",
                              "set(CMAKE_FIND_ROOT_PATH_MODE_PACKAGE BOTH)")
        if not cross_building(self):
            with tools_legacy.environment_append(self._emscripten_env):
                self.run("embuilder build MINIMAL", run_environment=True) # force cache population
                # the line below forces emscripten to accept the cache as-is, even after re-location
                # https://github.com/emscripten-core/emscripten/issues/15053#issuecomment-920950710
                os.remove(os.path.join(self._emscripten_env["EM_CACHE"], "sanity.txt"))

    def _define_tool_var(self, name, value):
        suffix = ".bat" if self.settings.os == "Windows" else ""
        path = os.path.join(self.package_folder, "bin", "upstream", "emscripten", f"{value}{suffix}")
        self._chmod_plus_x(path)
        self.output.info(f"Creating {name} environment variable: {path}")
        return path

    def package_info(self):
        self.cpp_info.bindirs.append(os.path.join("bin", "upstream", "emscripten"))
        self.cpp_info.includedirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.resdirs = []

        # If we are not building for Emscripten, probably we don't want to inject following environment variables,
        #   but it might be legit use cases... until we find them, let's be conservative.
        if not hasattr(self, "settings_target") or self.settings_target is None:
            return

        if self.settings_target.os != "Emscripten":
            self.output.warn(f"You've added {self.name}/{self.version} as a build requirement, while os={self.settings_target.os} != Emscripten")
            return

        toolchain = os.path.join(self.package_folder, "bin", "upstream", "emscripten", "cmake", "Modules", "Platform", "Emscripten.cmake")
        self.conf_info.prepend("tools.cmake.cmaketoolchain:user_toolchain", toolchain)

        self.buildenv_info.define_path("EMSDK", self.package_folder)
        self.buildenv_info.define_path("EMSCRIPTEN", os.path.join(self.package_folder, "bin", "upstream", "emscripten"))
        self.buildenv_info.define_path("EM_CONFIG", os.path.join(self.package_folder, "bin", ".emscripten"))
        self.buildenv_info.define_path("EM_CACHE", os.path.join(self.package_folder, "bin", ".emscripten_cache"))

        self.buildenv_info.define_path("CC", self._define_tool_var("CC", "emcc"))
        self.buildenv_info.define_path("CXX", self._define_tool_var("CXX", "em++"))
        self.buildenv_info.define_path("RANLIB", self._define_tool_var("RANLIB", "emranlib"))
        self.buildenv_info.define_path("AR", self._define_tool_var("AR", "emar"))

        self.cpp_info.builddirs = [
            "bin/releases/src",
            "bin/upstream/emscripten/cmake/Modules",
            "bin/upstream/emscripten/cmake/Modules/Platform",
            "bin/upstream/emscripten/system/lib/libunwind/cmake/Modules",
            "bin/upstream/emscripten/system/lib/libunwind/cmake",
            "bin/upstream/emscripten/tests/cmake/target_library",
            "bin/upstream/lib/cmake/llvm",
        ]

        # TODO: to remove in conan v2?
        self.output.info(f"Creating CONAN_CMAKE_TOOLCHAIN_FILE environment variable: {toolchain}")
        self.env_info.CONAN_CMAKE_TOOLCHAIN_FILE = toolchain
        self.env_info.CC = self._define_tool_var("CC", "emcc")
        self.env_info.CXX = self._define_tool_var("CXX", "em++")
        self.env_info.RANLIB = self._define_tool_var("RANLIB", "emranlib")
        self.env_info.AR = self._define_tool_var("AR", "emar")
        for var, val in self._emscripten_env.items():
            self.output.info(f"Creating {var} environment variable: {val}")
            setattr(self.env_info, var, val)
