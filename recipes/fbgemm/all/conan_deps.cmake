find_package(asmjit REQUIRED CONFIG)
find_package(cpuinfo REQUIRED CONFIG)
link_libraries(asmjit::asmjit cpuinfo::cpuinfo)
