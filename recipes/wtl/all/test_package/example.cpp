#include <iostream>
#include <atlbase.h>
#include <atlapp.h>

class TestHandler : public CIdleHandler {
	public:
		virtual BOOL OnIdle() override
		{
			std::cout << "Package test completed successfully";
			return FALSE;
		}
};

int main() {
	TestHandler handler;
	return handler.OnIdle();
}
