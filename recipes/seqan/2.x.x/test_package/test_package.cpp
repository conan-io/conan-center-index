// Demo program for clipping with Gaps objects.

#include <seqan/align.h>
#include <seqan/sequence.h>
#include <seqan/version.h>

#include <iostream>

#if SEQAN_VERSION_MINOR >= 5
using namespace seqan2;
#else
using namespace seqan;
#endif

int main()
{
    // Create sequence variable and gaps basd on sequence.
    CharString seq("ABCDEFGHIJ");
    Gaps<CharString> gaps(seq);

    // Insert gaps, the positions are in (clipped) view space.
    insertGaps(gaps, 2, 2);
    insertGap(gaps, 6);
    insertGap(gaps, 10);

    // Print to stdout.
    std::cout << "gaps\t" << gaps << "\n"
              << "seq \t" << seq << "\n\n";

    return 0;
}
