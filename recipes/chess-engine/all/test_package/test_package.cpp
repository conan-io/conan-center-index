#include <chessEngine.hpp>

int main() {
    Board board("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1");
    board.makeMove("e2", "e4");
    std::cout << board.toFen() << std::endl;
    return 0;
}
