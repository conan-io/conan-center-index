#include <seqan3/alphabet/nucleotide/dna4.hpp>
#include <seqan3/alphabet/views/complement.hpp>
#include <seqan3/core/debug_stream.hpp>

int main()
{
    using namespace seqan3::literals;

    std::vector<seqan3::dna4> seq = "AGTGTACGTAC"_dna4;

    seqan3::debug_stream << "Sequence: " << seq << '\n';
    seqan3::debug_stream << "Reverse complement: " << (seq | std::views::reverse | seqan3::views::complement) << '\n';

    return 0;
}
