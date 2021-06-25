#include <sdsl/bit_vectors.hpp>
#include <iostream>

int main()
{
    sdsl::bit_vector b(10000000, 0);
    b[8] = 1;
    sdsl::rank_support_v<> rb(&b);

    std::cout << rb(8) << std::endl;
    std::cout << rb(9) << std::endl;

    std::cout << "size of b in MB: " << sdsl::size_in_mega_bytes(b) << std::endl;
    std::cout << "size of rb in MB: " << sdsl::size_in_mega_bytes(rb) << std::endl;

    sdsl::rrr_vector<127> rrrb(b);
    sdsl::rrr_vector<127>::rank_1_type rank_rrrb(&rrrb);
    std::cout << rank_rrrb(8) << std::endl;
    std::cout << rank_rrrb(9) << std::endl;

    std::cout << "size of rrrb in MB: " << sdsl::size_in_mega_bytes(rrrb) << std::endl;
    std::cout << "size of rank_rrrb in MB: " << sdsl::size_in_mega_bytes(rank_rrrb) << std::endl;

    sdsl::rrr_vector<127>::select_1_type select_rrrb(&rrrb);
    std::cout << "position of first one in b: " << select_rrrb(1) << std::endl;

    sdsl::bit_vector x;
    x = sdsl::bit_vector(10000000, 1);

    sdsl::int_vector<> v(100, 5, 7);

    std::cout << "v[5]=" << v[5] << std::endl;
    v[5] = 120;
    std::cout << "v[5]=" << v[5] << std::endl;

    sdsl::int_vector<32> w(100, 4);

    sdsl::write_structure<sdsl::JSON_FORMAT>(rrrb, std::cout);
    std::cout << std::endl;

    return 0;
}
