# Work-around for https://github.com/wjwwood/serial/issues/135

function(catkin_package)
endfunction()

set(CATKIN_PACKAGE_LIB_DESTINATION lib)
set(CATKIN_GLOBAL_BIN_DESTINATION bin)
set(CATKIN_GLOBAL_INCLUDE_DESTINATION include)
set(CATKIN_ENABLE_TESTING OFF)
