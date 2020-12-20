SET( ACADO_QPOASES_EMBEDDED_SOURCES 
	${CMAKE_CURRENT_LIST_DIR}/../share/acado/external_packages/qpoases/SRC/Bounds.cpp
	${CMAKE_CURRENT_LIST_DIR}/../share/acado/external_packages/qpoases/SRC/CyclingManager.cpp 
	${CMAKE_CURRENT_LIST_DIR}/../share/acado/external_packages/qpoases/SRC/MessageHandling.cpp
	${CMAKE_CURRENT_LIST_DIR}/../share/acado/external_packages/qpoases/SRC/QProblem.cpp
	${CMAKE_CURRENT_LIST_DIR}/../share/acado/external_packages/qpoases/SRC/Utils.cpp
	${CMAKE_CURRENT_LIST_DIR}/../share/acado/external_packages/qpoases/SRC/Constraints.cpp
	${CMAKE_CURRENT_LIST_DIR}/../share/acado/external_packages/qpoases/SRC/Indexlist.cpp	     
	${CMAKE_CURRENT_LIST_DIR}/../share/acado/external_packages/qpoases/SRC/QProblemB.cpp
	${CMAKE_CURRENT_LIST_DIR}/../share/acado/external_packages/qpoases/SRC/SubjectTo.cpp
	${CMAKE_CURRENT_LIST_DIR}/../share/acado/external_packages/qpoases/SRC/EXTRAS/SolutionAnalysis.cpp
)
SET( ACADO_QPOASES_EMBEDDED_INC_DIRS 
	${CMAKE_CURRENT_LIST_DIR}/../share/acado/external_packages/qpoases/
	${CMAKE_CURRENT_LIST_DIR}/../share/acado/external_packages/qpoases/INCLUDE
	${CMAKE_CURRENT_LIST_DIR}/../share/acado/external_packages/qpoases/SRC
)
