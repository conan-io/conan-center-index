from conans import ConanFile, tools
import os
import json

required_conan_version = ">=1.33.0"


class EmSDKConan(ConanFile):
    name = "emsdk"
    description = "Emscripten SDK. Emscripten is an Open Source LLVM to JavaScript compiler"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/kripken/emscripten"
    topics = ("emsdk", "emscripten", "sdk")
    license = "MIT"
    settings = "os", "arch"

    short_paths = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def requirements(self):
        self.requires("nodejs/16.3.0")
        # self.requires("python")  # FIXME: Not available as Conan package
        # self.requires("wasm")  # FIXME: Not available as Conan package

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    @staticmethod
    def _chmod_plus_x(filename):
        if os.name == "posix":
            os.chmod(filename, os.stat(filename).st_mode | 0o111)

    def _tools_for_version(self):
        ret = {}
        # Select release-upstream from version (wasm-binaries)
        with open(os.path.join(self.build_folder, self._source_subfolder, "emscripten-releases-tags.json"), 'r') as f:
            data = json.load(f)
            ret['wasm'] = "releases-upstream-{}-64bit".format(data["releases"][self.version])
        # Select python and node versions
        with open(os.path.join(self.build_folder, self._source_subfolder, "emsdk_manifest.json"), 'r') as f:
            data = json.load(f)
            tools = data["tools"]
            if self.settings.os == "Windows":
                python = next((it for it in tools if (it["id"] == "python" and not it.get("is_old", False))), None)
                ret["python"] = "python-{}-64bit".format(python["version"])
            node = next((it for it in tools if (it["id"] == "node" and not it.get("is_old", False))), None)
            ret["nodejs"] = "node-{}-64bit".format(node["version"])
        return ret

    def build(self):
        with tools.files.chdir(self, self._source_subfolder):
            emsdk = "emsdk.bat" if tools.os_info.is_windows else "./emsdk"
            self._chmod_plus_x("emsdk")

            # Install required tools
            required_tools = self._tools_for_version()
            for key, value in required_tools.items():
                if key != 'nodejs':
                    self.run("%s install %s" % (emsdk, value))
                    self.run("%s activate %s" % (emsdk, value))

    @property
    def _emscripten_env(self):
        return {"PATH": [self.package_folder, os.path.join(self.package_folder, "bin", "upstream", "emscripten")],
                "EMSDK": self.package_folder,
                "EMSCRIPTEN": os.path.join(self.package_folder, "bin", "upstream", "emscripten"),
                "EM_CONFIG": os.path.join(self.package_folder, "bin", ".emscripten"),
                "EM_CACHE": os.path.join(self.package_folder,  "bin", ".emscripten_cache")}

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy(pattern="*", dst="bin", src=self._source_subfolder)
        emscripten = os.path.join(self.package_folder, "bin", "upstream", "emscripten")
        toolchain = os.path.join(emscripten, "cmake", "Modules", "Platform", "Emscripten.cmake")
        # FIXME: conan should add the root of conan package requirements to CMAKE_PREFIX_PATH (LIBRARY/INCLUDE -> ONLY; PROGRAM -> NEVER)
        # allow to find conan libraries
        tools.files.replace_in_file(self, toolchain,
                              "set(CMAKE_FIND_ROOT_PATH_MODE_LIBRARY ONLY)",
                              "set(CMAKE_FIND_ROOT_PATH_MODE_LIBRARY BOTH)")
        tools.files.replace_in_file(self, toolchain,
                              "set(CMAKE_FIND_ROOT_PATH_MODE_INCLUDE ONLY)",
                              "set(CMAKE_FIND_ROOT_PATH_MODE_INCLUDE BOTH)")
        tools.files.replace_in_file(self, toolchain,
                              "set(CMAKE_FIND_ROOT_PATH_MODE_PACKAGE ONLY)",
                              "set(CMAKE_FIND_ROOT_PATH_MODE_PACKAGE BOTH)")
        if not tools.cross_building(self):
            with tools.environment_append(self._emscripten_env):
                self.run("embuilder build MINIMAL", run_environment=True) # force cache population
                # the line below forces emscripten to accept the cache as-is, even after re-location
                # https://github.com/emscripten-core/emscripten/issues/15053#issuecomment-920950710
                os.remove(os.path.join(self._emscripten_env["EM_CACHE"], "sanity.txt"))



    def _define_tool_var(self, name, value):
        suffix = ".bat" if self.settings.os == "Windows" else ""
        path = os.path.join(self.package_folder, "bin", "upstream",
                            "emscripten", "%s%s" % (value, suffix))
        self._chmod_plus_x(path)
        self.output.info("Creating %s environment variable: %s" % (name, path))
        return path

    def package_info(self):
        self.cpp_info.includedirs = []
        self.cpp_info.libdirs = []

        for var, val in self._emscripten_env.items():
            self.output.info("Creating %s environment variable: %s" % (var, val))
            setattr(self.env_info, var, val)

        # If we are not building for Emscripten, probably we don't want to inject following environment variables,
        #   but it might be legit use cases... until we find them, let's be conservative.
        if not hasattr(self, "settings_target") or self.settings_target is None:
            return

        if self.settings_target.os != "Emscripten":
            self.output.warn("You've added {}/{} as a build requirement, while os={} != Emscripten".format(self.name, self.version, self.settings_target.os))
            return


        toolchain = os.path.join(self.package_folder, "bin", "upstream", "emscripten", "cmake", "Modules", "Platform", "Emscripten.cmake")
        self.output.info("Creating CONAN_CMAKE_TOOLCHAIN_FILE environment variable: %s" % toolchain)
        self.env_info.CONAN_CMAKE_TOOLCHAIN_FILE = toolchain

        self.env_info.CC = self._define_tool_var("CC", "emcc")
        self.env_info.CXX = self._define_tool_var("CXX", "em++")
        self.env_info.RANLIB = self._define_tool_var("RANLIB", "emranlib")
        self.env_info.AR = self._define_tool_var("AR", "emar")
        self.cpp_info.builddirs = [
            "bin/releases/src",
            "bin/upstream/emscripten/cmake/Modules",
            "bin/upstream/emscripten/cmake/Modules/Platform",
            "bin/upstream/emscripten/system/lib/libunwind/cmake/Modules",
            "bin/upstream/emscripten/system/lib/libunwind/cmake",
            "bin/upstream/emscripten/tests/cmake/target_library",
            "bin/upstream/lib/cmake/llvm",
        ]
