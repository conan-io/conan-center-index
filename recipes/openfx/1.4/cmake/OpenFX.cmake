# Add a new OFX plugin target
# Arguments: TARGET
function(add_ofx_plugin TARGET)
	add_library(${TARGET} SHARED)
	set_target_properties(${TARGET} PROPERTIES SUFFIX ".ofx" PREFIX "")

	if(NOT DEFINED OFX_SUPPORT_SYMBOLS_DIR)
		if (NOT DEFINED CONAN_LIB_DIRS_OPENFX)
			message(FATAL_ERROR "Define OFX_SUPPORT_SYMBOLS_DIR to use add_ofx_plugin().")
		endif()
		set(OFX_SUPPORT_SYMBOLS_DIR ${CONAN_LIB_DIRS_OPENFX}/symbols)
	endif()

	# Add extra flags to the link step of the plugin
	if(APPLE)
		set_target_properties(${TARGET} PROPERTIES LINK_FLAGS "-bundle -fvisibility=hidden -exported_symbols_list,${OFX_SUPPORT_SYMBOLS_DIR}/osx.symbols")
	elseif(WIN32)
		set_target_properties(${TARGET} PROPERTIES LINK_FLAGS "/def:${OFX_SUPPORT_SYMBOLS_DIR}/windows.symbols")
	else()
		set_target_properties(${TARGET} PROPERTIES LINK_FLAGS "-Wl,-fvisibility=hidden,--version-script=${OFX_SUPPORT_SYMBOLS_DIR}/linux.symbols")
	endif()
endfunction()
