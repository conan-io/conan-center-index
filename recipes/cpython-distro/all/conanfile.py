import os
from conans import ConanFile, tools
from conans.errors import ConanInvalidConfiguration


class CpythonDistro(ConanFile):
    name = 'cpython-distro'
    settings = 'os', 'arch'
    description = 'CPython 2.7'
    exports_sources = ['patches/*', 'requirements.txt']
    short_paths = True

    _unpacked_folder = 'unpacked'

    @property
    def msi(self):
        return os.path.join(self.source_folder, 'python.msi')

    @property
    def get_pip(self):
        return os.path.join(self.source_folder, 'get_pip.py')

    @property
    def original_version(self):
        if 'dssl' in self.version:
            v = self.version.split('.')
            return '.'.join(v[:-1])
        return self.version

    def configure(self):
        if not self.settings.os == 'Windows':
            raise ConanInvalidConfiguration('Only Windows is supported')
        if not self.settings.arch == 'x86_64':
            raise ConanInvalidConfiguration('Only x86_x64 is supported')


    def source(self):
        arch = str(self.settings.arch)
        url_and_sha = self.conan_data['sources'][self.original_version][arch]
        tools.download(**url_and_sha, filename=self.msi)
        tools.download(url='https://bootstrap.pypa.io/pip/2.7/get-pip.py', filename=self.get_pip)
        unpacked = os.path.join(self.source_folder, self._unpacked_folder)

        self.output.info('unpacking python.msi to '+unpacked)
        self.run('msiexec /a {msi} /qb TARGETDIR={unpacked}'.format(msi=self.msi, unpacked=unpacked))

        self.output.info('applying header patches')
        for patch in self.conan_data.get('patches', {}).get(self.original_version, []):
            tools.patch(**patch, base_path=self._unpacked_folder)


    def build(self):
        unpacked = os.path.join(self.build_folder, self._unpacked_folder)

        py = os.path.join(unpacked, 'python.exe')
        py2 = os.path.join(unpacked, 'python2.exe')
        self.output.info('renaming {py} to {py2}'.format(py=py, py2=py2))
        tools.rename(py, py2)

        self.output.info('installing pip')
        self.run('{pyexe} {pip} --no-warn-script-location'.format(pyexe=py2, pip=self.get_pip))

        requirements = os.path.join(self.build_folder, 'requirements.txt')
        pip = '{pyexe} -m pip install -r {req} --ignore-installed'.format(req=requirements, pyexe=py2)
        self.output.info('running pip install:\n'+pip)
        self.run(pip)


    def package(self):
        self.copy('*', src=self._unpacked_folder, excludes=[
            'Doc', # extra documentation files
            'python.msi', # uninstaller
            'Scripts' # .exe files rely on absolute paths to python.exe and are not relocatable
        ])


    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.bindirs = [self.package_folder]

        self.output.info("env_info.PATH: {}".format(self.package_folder))
        self.env_info.PATH.append(self.package_folder)
        self.output.info("env_info.CONAN_CPYTHON_DISTRO_PATH: {}".format(self.package_folder))
        self.env_info.CONAN_CPYTHON_DISTRO_PATH = self.package_folder


    def package_id(self):
        self.info.settings.build_type = 'Any'
        self.info.settings.compiler = 'Any'
