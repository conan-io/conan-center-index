project('test_package', 'cpp')
qt6 = import('qt6')
qt6_dep = dependency('qt6', modules: ['Core', 'Network', 'Sql', 'Concurrent', 'Xml'])
moc_files = qt6.preprocess(moc_headers : 'greeter.h', qresources : 'example.qrc')
executable('test_package', 'test_package.cpp', moc_files,
           dependencies : qt6_dep)
