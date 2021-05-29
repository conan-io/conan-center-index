SET( ACADO_QPOASES_EMBEDDED_SOURCES 
	${CMAKE_CURRENT_LIST_DIR}/qpoases/SRC/Bounds.cpp
	${CMAKE_CURRENT_LIST_DIR}/qpoases/SRC/CyclingManager.cpp 
	${CMAKE_CURRENT_LIST_DIR}/qpoases/SRC/MessageHandling.cpp
	${CMAKE_CURRENT_LIST_DIR}/qpoases/SRC/QProblem.cpp
	${CMAKE_CURRENT_LIST_DIR}/qpoases/SRC/Utils.cpp
	${CMAKE_CURRENT_LIST_DIR}/qpoases/SRC/Constraints.cpp
	${CMAKE_CURRENT_LIST_DIR}/qpoases/SRC/Indexlist.cpp	     
	${CMAKE_CURRENT_LIST_DIR}/qpoases/SRC/QProblemB.cpp
	${CMAKE_CURRENT_LIST_DIR}/qpoases/SRC/SubjectTo.cpp
	${CMAKE_CURRENT_LIST_DIR}/qpoases/SRC/EXTRAS/SolutionAnalysis.cpp
)
SET( ACADO_QPOASES_EMBEDDED_INC_DIRS 
	${CMAKE_CURRENT_LIST_DIR}/qpoases/
	${CMAKE_CURRENT_LIST_DIR}/qpoases/INCLUDE
	${CMAKE_CURRENT_LIST_DIR}/qpoases/SRC
)
