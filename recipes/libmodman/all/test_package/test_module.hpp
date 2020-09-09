#include "libmodman/module_manager.hpp"

class __MM_DLL_EXPORT my_extension : public libmodman::extension<my_extension> {
public:
	virtual int expensive_operation(int a) const = 0;
};
