#include <AppxPackaging.hpp>

LPVOID STDMETHODCALLTYPE MyAllocate(SIZE_T cb) {
	return std::malloc(cb);
}

void STDMETHODCALLTYPE MyFree(LPVOID pv) {
	std::free(pv);
}

int main() {
	IAppxFactory* appxFactory;

	HRESULT creationResult = CoCreateAppxFactoryWithHeap(
		MyAllocate,
		MyFree,
		MSIX_VALIDATION_OPTION::MSIX_VALIDATION_OPTION_FULL,
		&appxFactory
	);

	if (FAILED(creationResult)) {
		return creationResult;
	}

	return 0;
}
