project('test_package', 'cpp')
qt5 = import('qt5')
qt5_dep = dependency('qt5', modules: ['Core', 'Network'])
moc_files = qt5.preprocess(moc_headers : 'greeter.h', qresources : 'example.qrc')
executable('test_package', 'test_package.cpp', moc_files,
           dependencies : qt5_dep)
