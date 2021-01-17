import os
from conans import ConanFile, tools

class Recipe(ConanFile):
    name = "qt"
    settings = "os", "arch", "compiler", "build_type"

    short_paths = True
    _source_subfolder = "source_subfolder"

    options = {
        'commercial': [True, False],
        'target': [None, 'wasm'],

        'qtbase': [True, False],
        'qtdeclarative': [True, False],
        'qt3d': [True, False],
        'qtcanvas3d': [True, False],
    }
    default_options = {
        'commercial': False,
        'target': None,

        'qtbase': True,
        'qtdeclarative': True,
        'qt3d': False,
        'qtcanvas3d': False
    }

    def _modules_activated(self):
        for opt in self.options:
            option_name = str(opt)
            if option_name.startswith('qt') and getattr(self.options, option_name):
                yield 'module-{}'.format(option_name)

    def build_requirements(self):
        if self.options.target == 'wasm':
            emsdk = {'5.15.2': 'emsdk/1.39.8'}.get(self.version)
            #self.build_requires('emsdk/2.0.12')
            self.build_requires(emsdk)

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_folder = "qt-everywhere-src-%s" % self.version
        os.rename(extracted_folder, self._source_subfolder)

    def build(self):
        with tools.chdir(self._source_subfolder):
            if self.options.target == 'wasm':
                self._build_emscripten()
            else:
                raise Exception("Not implemented")

            # Probably common to all builds
            self.run('make {}'.format(' '.join(self._modules_activated())))
            self.run('make install')

    def _build_emscripten(self):
        emsdk = 'em++' if self.settings.os == 'Windows' else 'emcc'
        self.run('{} --version'.format(emsdk), run_environment=True)

        if self.settings.os == 'Windows':
            raise Exception("Not implemented")
        else:
            args = ["-confirm-license", "-nomake examples", "-nomake tests", "-prefix", self.package_folder]
            if self.options.commercial:
                args.append("-commercial")
            else:
                args.append("-opensource")
            self.run('./configure -xplatform wasm-emscripten {}'.format(' '.join(args)), run_environment=True)

    def package_info(self):
        # As build-requires I want to use 'qmake'
        self.env_info.PATH.append(os.path.join(self.package_folder))
