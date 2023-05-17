#include "ikcp.h"

#include <algorithm>
#include <iostream>
#include <iterator>
#include <deque>
#include <random>
#include <vector>

class Channel {
    std::deque<char> buffer_;
public:
    void send(const char *buf, size_t len) {
        std::back_insert_iterator<std::deque<char>> back_it{buffer_};
        std::copy(buf, buf+len, back_it);
    }
    std::vector<char> recv(size_t len) {
        std::vector<char> res;
        len = std::min(len, buffer_.size());
        if (len == 0) len = buffer_.size();
        std::back_insert_iterator<std::vector<char>> back_it{res};
        std::copy(std::begin(buffer_), std::end(buffer_), back_it);
        buffer_.erase(std::begin(buffer_), std::begin(buffer_)+len);
        return res;
    }
};

struct Connection {
    Channel     *input;
    Channel     *output;
    int     id;
};

static int net_output(const char *buf, int len, ikcpcb *kcp, void *user)
{
    Connection *conn = static_cast<Connection *>(user);
    std::cerr << "net_output(len=" << len << ", id=" << conn->id << ")\n";
    conn->output->send(buf, len);
	return 0;
}

int main() {
    std::default_random_engine random{0};

    Channel net1;
    Channel net2;
    Connection c1{&net1, &net2, 1};
    Connection c2{&net2, &net1, 2};

	ikcpcb *kcp1 = ikcp_create(0x11223344, &c1);
	ikcpcb *kcp2 = ikcp_create(0x11223344, &c2);

	kcp1->output = net_output;
	kcp2->output = net_output;

	ikcp_wndsize(kcp1, 128, 128);
	ikcp_wndsize(kcp2, 128, 128);

    char buffer[2048];

	for (size_t time=0; time != 10000; time += 1) {
	    ikcp_update(kcp1, time);
	    ikcp_update(kcp2, time);

        while (random() % 3) {
	        ikcp_send(kcp1, buffer, 512);
        }

        while (true) {
            auto data = c2.input->recv(512);
            if (data.size() == 0) break;
            ikcp_input(kcp2, data.data(), data.size());
        }

        while (true) {
            auto data = c1.input->recv(512);
            if (data.size() == 0) break;
            ikcp_input(kcp2, data.data(), data.size());
        }
	}
    return 0;
}
