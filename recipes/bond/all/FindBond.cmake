# find_path(BOND_INCLUDE_DIR NAMES bond PATHS ${CONAN_INCLUDE_DIRS_BOND})
find_library(BOND_LIBRARY NAMES ${CONAN_LIBS_BOND} PATHS ${CONAN_LIB_DIRS_BOND})
find_file(BOND_GBC NAMES gbc.exe gbc PATHS ${CONAN_BIN_DIRS_BOND})

set(BOND_FOUND TRUE)
set(BOND_INCLUDE_DIRS ${CONAN_INCLUDE_DIRS_BOND})
set(BOND_LIBRARIES ${BOND_LIBRARY})
set(BOND_GBC ${BOND_GBC})
mark_as_advanced(BOND_LIBRARY BOND_INCLUDE_DIR)
