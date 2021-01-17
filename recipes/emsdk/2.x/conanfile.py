import os
import re
from six import StringIO
import shutil
from contextlib import contextmanager
from conans import ConanFile, tools
from conans.errors import ConanException


class Recipe(ConanFile):
    name = "emsdk"
    description = "Emscripten is an Open Source LLVM to JavaScript compiler"
    topics = ("conan", "emsdk", "emscripten", "installer", "sdk")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/emscripten-core/emsdk"
    license = "MIT"
    settings = "os", "arch"

    short_paths = True
    _source_subfolder = "source_subfolder"

    @property
    def _emsdk_exec(self):
        return 'emsdk.bat' if self.settings.os == "Windows" else './emsdk'

    @property
    def _node_version(self):
        return '12.18.1-64bit'

    @property
    def _python_version(self):
        return '3.7.4-2-64bit'

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_folder = "emsdk-%s" % self.version
        os.rename(extracted_folder, self._source_subfolder)

    def _install_tool(self, tool_name, directory, n_retries=3):
        retries = 0
        while retries < n_retries:
            retries += 1
            mybuf = StringIO()
            self.run('{} install {}'.format(self._emsdk_exec, tool_name), output=mybuf)
            if 'failed with error code 1' not in mybuf.getvalue():
                self.output.info(mybuf.getvalue())
                self.output.info("Suceed to install {} in retry {}/{}".format(tool_name, retries, n_retries))
                return
            else:
                self.output.info(mybuf.getvalue())
                self.output.warn("Failed to install {} in retry {}/{}".format(tool_name, retries, n_retries))
                if os.path.exists(directory):
                    shutil.rmtree(directory)

    def build(self):
        with tools.chdir(self._source_subfolder):
            # En Macos estos install fallan como una escopeta de feria
            self._install_tool('node-' + self._node_version, 'node')
            self._install_tool('python-' + self._python_version, 'python')
            self._install_tool(self.version, 'upstream')
            self.run('{} activate {}'.format(self._emsdk_exec, self.version))

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy(pattern='*', dst='.', src=self._source_subfolder) # TODO: Not everything is needed
    
    def package_info(self):
        # Usable only as a build-require, it populates the same environment as activating 'emsdk_env.sh'
        self.env_info.PATH.append(self.package_folder)
        self.env_info.PATH.append(os.path.join(self.package_folder, 'upstream', 'emscripten'))
        self.env_info.PATH.append(os.path.join(self.package_folder, 'node', self._node_version, 'bin'))
        self.env_info.PATH.append(os.path.join(self.package_folder, 'python', self._python_version, 'bin'))

        self.env_info.EMSDK = os.path.join(self.package_folder)
        self.env_info.EM_CONFIG = os.path.join(self.package_folder, '.emscripten')
        self.env_info.EM_CACHE = os.path.join(self.package_folder, 'upstream', 'emscripten', 'cache')
        self.env_info.EMSDK_NODE = os.path.join(self.package_folder, 'node', self._node_version, 'bin', 'node')
        self.env_info.EMSDK_PYTHON = os.path.join(self.package_folder, 'python', self._python_version.replace('-64bit', '_64bit'), 'bin', 'python3')
        self.env_info.SSL_CERT_FILE = os.path.join(self.package_folder, 'python', self._python_version.replace('-64bit', '_64bit'), 'lib', 'python3.7', 'site-package', 'certifi', 'cacert.pem')
