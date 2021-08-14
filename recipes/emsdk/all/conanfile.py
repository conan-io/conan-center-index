from conans import ConanFile, tools
import os

required_conan_version = ">=1.33.0"


class EmSDKConan(ConanFile):
    name = "emsdk"
    description = "Emscripten is an Open Source LLVM to JavaScript compiler"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/kripken/emscripten"
    topics = ("conan", "emsdk", "emscripten", "sdk")
    license = "MIT"
    settings = "os"

    short_paths = True

    @ property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    @ staticmethod
    def _create_dummy_file(directory):
        tools.save(os.path.join(directory, "dummy"), "\n")

    @ staticmethod
    def _touch(filename):
        if not os.path.isfile(filename):
            tools.save(filename, "\n")

    @ staticmethod
    def _chmod_plus_x(filename):
        if os.name == 'posix':
            os.chmod(filename, os.stat(filename).st_mode | 0o111)

    def build(self):
        with tools.chdir(self._source_subfolder):
            emsdk = 'emsdk.bat' if os.name == 'nt' else './emsdk'
            if os.path.isfile("python_selector"):
                self._chmod_plus_x("python_selector")
            self._chmod_plus_x('emsdk')
            self.run('%s update' % emsdk)
            if os.path.isfile("python_selector"):
                self._chmod_plus_x("python_selector")
            self._chmod_plus_x('emsdk')

            self.run('%s install %s' % (emsdk, self.version))
            self.run('%s activate %s --embedded' % (emsdk, self.version))

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses",
                  src=self._source_subfolder)
        self.copy(pattern='*', dst='bin',
                  src=self._source_subfolder, excludes=('*.pc', '*Find*.cmake', '*Box2DConfig.cmake', '*CTestConfig.cmake',
                                                        '*concrt140.dll', '*msvcr100.dll', '*concrt140d.dll', '*msvcp140.dll', '*msvcp140d.dll', '*vcruntime140.dll',
                                                        '*vcruntime140_1.dll', '*vcruntime140_1d.dll', '*vcruntime140d.dl'))
        emsdk = self.package_folder
        emscripten = os.path.join(emsdk, 'bin', 'upstream', 'emscripten')
        toolchain = os.path.join(
            emscripten, 'cmake', 'Modules', 'Platform', 'Emscripten.cmake')
        # allow to find conan libraries
        tools.replace_in_file(toolchain,
                              "set(CMAKE_FIND_ROOT_PATH_MODE_LIBRARY ONLY)",
                              "set(CMAKE_FIND_ROOT_PATH_MODE_LIBRARY BOTH)")
        tools.replace_in_file(toolchain,
                              "set(CMAKE_FIND_ROOT_PATH_MODE_INCLUDE ONLY)",
                              "set(CMAKE_FIND_ROOT_PATH_MODE_INCLUDE BOTH)")
        tools.replace_in_file(toolchain,
                              "set(CMAKE_FIND_ROOT_PATH_MODE_PACKAGE ONLY)",
                              "set(CMAKE_FIND_ROOT_PATH_MODE_PACKAGE BOTH)")

    def _define_tool_var(self, name, value):
        suffix = '.bat' if self.settings.os == "Windows" else ''
        path = os.path.join(self.package_folder, 'bin', 'upstream',
                            'emscripten', '%s%s' % (value, suffix))
        self._chmod_plus_x(path)
        self.output.info('Creating %s environment variable: %s' % (name, path))
        return path

    def package_info(self):
        emsdk = self.package_folder
        em_config = os.path.join(emsdk, 'bin', '.emscripten')
        emscripten = os.path.join(emsdk, 'bin', 'upstream', 'emscripten')
        em_cache = os.path.join(emsdk,  'bin', '.emscripten_cache')
        toolchain = os.path.join(
            emscripten, 'cmake', 'Modules', 'Platform', 'Emscripten.cmake')

        self.output.info('Appending PATH environment variable: %s' % emsdk)
        self.env_info.PATH.append(emsdk)

        self.output.info(
            'Appending PATH environment variable: %s' % emscripten)
        self.env_info.PATH.append(emscripten)

        self.output.info('Creating EMSDK environment variable: %s' % emsdk)
        self.env_info.EMSDK = emsdk

        self.output.info(
            'Creating EMSCRIPTEN environment variable: %s' % emscripten)
        self.env_info.EMSCRIPTEN = emscripten

        self.output.info(
            'Creating EM_CONFIG environment variable: %s' % em_config)
        self.env_info.EM_CONFIG = em_config

        self.output.info(
            'Creating EM_CACHE environment variable: %s' % em_cache)
        self.env_info.EM_CACHE = em_cache

        self.output.info(
            'Creating CONAN_CMAKE_TOOLCHAIN_FILE environment variable: %s' % toolchain)
        self.env_info.CONAN_CMAKE_TOOLCHAIN_FILE = toolchain

        self.env_info.CC = self._define_tool_var('CC', 'emcc')
        self.env_info.CXX = self._define_tool_var('CXX', 'em++')
        self.env_info.RANLIB = self._define_tool_var('RANLIB', 'emranlib')
        self.env_info.AR = self._define_tool_var('AR', 'emar')
        self.cpp_info.builddirs = ['bin/releases/src/', 'bin/upstream/emscripten/cmake/Modules/', 'bin/upstream/emscripten/cmake/Modules/Platform/', 'bin/upstream/emscripten/system/lib/libunwind/cmake/Modules/',
                                   'bin/upstream/emscripten/system/lib/libunwind/cmake/', 'bin/upstream/emscripten/tests/cmake/target_library/', 'bin/upstream/lib/cmake/llvm/']
