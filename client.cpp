#include <iostream>
#include <cstring>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <unistd.h>

int main() {
    // Create a TCP socket
    int sock = socket(AF_INET, SOCK_STREAM, 0);
    if (sock == -1) {
        std::cerr << "Error creating socket\n";
        return 1;
    }

    // Set up the server address
    sockaddr_in server_addr;
    std::memset(&server_addr, 0, sizeof(server_addr));
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(9999); // Use port 9999
    if (inet_pton(AF_INET, "127.0.0.1", &server_addr.sin_addr) == -1) {
        std::cerr << "Error setting server address\n";
        return 1;
    }

    // Connect to the server
    if (connect(sock, reinterpret_cast<sockaddr*>(&server_addr), sizeof(server_addr)) == -1) {
        std::cerr << "Error connecting to server\n";
        return 1;
    }

    // Retrieve the local socket address and port
    sockaddr_in local_address;
    socklen_t local_address_length = sizeof(local_address);
    if (getsockname(sock, (sockaddr*) &local_address, &local_address_length) == -1) {
        std::cerr << "Error getting local socket address\n";
        return 1;
    }

    char hello_message[1024];
    int bytes_sent = snprintf(
        hello_message, 1024, "%s:%d\n", 
        inet_ntoa(local_address.sin_addr), ntohs(local_address.sin_port));

    if (send(sock, hello_message, bytes_sent, 0) == -1) {
        std::cerr << "Error sending message1\n";
        return 1;
    }

    // Receive data from the server
    const int max_buffer_size = 1024;
    char buffer[max_buffer_size];
    int bytes_received = 0;
    while (true) {
        int bytes = recv(sock, buffer + bytes_received, 1, 0);
        if (bytes == -1) {
            std::cerr << "Error receiving data from server\n";
            return 1;
        } else if (bytes == 0) {
            // Connection closed by server
            break;
        } else {
            bytes_received += bytes;
            if (bytes_received == max_buffer_size) {
                // Buffer full, increase its size or process the data
                std::cerr << "Received message is too long for the buffer\n";
                return 1;
            } else if (buffer[bytes_received - 1] == '\n') {
                // End of message received
                break;
            }
        }
    }

    // Print the received data
    buffer[bytes_received-1] = '\0';
    std::cout << "Received " << bytes_received << " bytes from server: " << buffer << "\n";

    // Send a response to the server
    const char* message2 = "Goodbye, server!\n";
    if (send(sock, message2, std::strlen(message2), 0) == -1) {
        std::cerr << "Error sending message2\n";
        return 1;
    }

    // Close the socket
    close(sock);

    return 0;
}
