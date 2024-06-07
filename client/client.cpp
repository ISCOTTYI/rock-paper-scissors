#include <iostream>
#include <cstring>
#include <cstdlib>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <cmath>
#include <sstream>
#include <regex>
#include <vector>

char PLAYER_ID;
const int MAX_X = 400;
const int MIN_X = 0;
const int MAX_Y = 400;
const int MIN_Y = 0;
const int R = 10;

std::string NICKNAME = "[SET YOUR TEAM NAME HERE]";

std::string make_move(std::string &game_state)
{
    // Write your code here
    //        |
    //        |
    //       \ /
    //        v
    std::string move;
    return move;
}

int main()
{
    // Create a TCP socket
    int sock = socket(AF_INET, SOCK_STREAM, 0);
    if (sock == -1)
    {
        std::cerr << "Error creating socket\n";
        return 1;
    }

    // Set up the server address
    sockaddr_in server_addr;
    std::memset(&server_addr, 0, sizeof(server_addr));
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(9999);
    if (inet_pton(AF_INET, "127.0.0.1", &server_addr.sin_addr) == -1)
    {
        std::cerr << "Error setting server address\n";
        return 1;
    }

    // Connect to the server
    if (connect(sock, reinterpret_cast<sockaddr *>(&server_addr), sizeof(server_addr)) == -1)
    {
        std::cerr << "Error connecting to server\n";
        return 1;
    }

    // Retrieve the local socket address and port
    sockaddr_in local_address;
    socklen_t local_address_length = sizeof(local_address);
    if (getsockname(sock, (sockaddr *)&local_address, &local_address_length) == -1)
    {
        std::cerr << "Error getting local socket address\n";
        return 1;
    }

    char addr_msg[1024];
    int bytes_sent = snprintf(
        addr_msg, 1024, "%s:%d",
        inet_ntoa(local_address.sin_addr), ntohs(local_address.sin_port));

    // Append player nickname to address message
    NICKNAME = "~" + NICKNAME + "\n";
    if (sizeof(addr_msg) - strlen(addr_msg) > NICKNAME.length()) {
        std::strcat(addr_msg, NICKNAME.c_str());
        bytes_sent = bytes_sent + NICKNAME.length();
    } else {
        std::cerr << "Not enough space in the char array to append the string." << std::endl;
    }

    std::cout << addr_msg << std::endl;

    if (send(sock, addr_msg, bytes_sent, 0) == -1)
    {
        std::cerr << "Error sending message1\n";
        return 1;
    }

    char buffer[2];
    int bytes_received = recv(sock, buffer, 2, 0);
    if (bytes_received == -1)
    {
        std::cerr << "Error receiving data from server\n";
        return 1;
    }
    else
    {
        PLAYER_ID = buffer[0];
    }
    std::cout << "Player ID is: "<< PLAYER_ID << std::endl;

    while (true)
    {
        // Receive data from the server
        int max_buffer_size = 4096;
        std::vector<char> buffer(max_buffer_size);
        // char buffer[max_buffer_size];
        int bytes_received = 0;
        while (true)
        {
            if (bytes_received >= max_buffer_size)
            {
                buffer.resize(buffer.size() + max_buffer_size / 2);
            }
            // Receive one byte at a time
            int bytes = recv(sock, &buffer[bytes_received], 1, 0);
            if (bytes == -1)
            {
                std::cerr << "Error receiving data from server\n";
                return 1;
            }
            else if (bytes == 0)
            {
                // Connection closed by server
                break;
            }
            else
            {
                bytes_received += bytes;
                if (buffer[bytes_received - 1] == '\n')
                {
                    // End of message received
                    break;
                }
            }
        }
        // Handle received game state
        buffer[bytes_received - 1] = '\0';
        std::string buffer_str = std::string(&buffer[0]);

        // Send a response to the server
        std::string move = make_move(buffer_str);
        if (move.back() != '\n') {
            move += '\n';
        }

        if (send(sock, move.c_str(), std::strlen(move.c_str()), 0) == -1)
        {
            std::cerr << "Error sending move\n";
            return 1;
        }
    }
    return 0;
}
