#include "Iir.h"

int main()
{
	const int order = 8;

	// Butterworth lowpass
	Iir::Butterworth::LowPass<order> f;

	return 0;
}

