# Only used on Windows and iOS

set(entrypoint_conditions "$<NOT:$<BOOL:$<TARGET_PROPERTY:qt_no_entrypoint>>>")
list(APPEND entrypoint_conditions "$<STREQUAL:$<TARGET_PROPERTY:TYPE>,EXECUTABLE>")
if(WIN32)
    list(APPEND entrypoint_conditions "$<BOOL:$<TARGET_PROPERTY:WIN32_EXECUTABLE>>")
endif()
list(JOIN entrypoint_conditions "," entrypoint_conditions)
set(entrypoint_conditions "$<AND:${entrypoint_conditions}>")
set_property(
    TARGET ${QT_CMAKE_EXPORT_NAMESPACE}::Core
    APPEND PROPERTY INTERFACE_LINK_LIBRARIES "$<${entrypoint_conditions}:${QT_CMAKE_EXPORT_NAMESPACE}::EntryPointPrivate>"
)
