# Threaded HTTP Server and Load Balancer

This project contains an HTTP Server utilizing multithreading and a Load Balancer, each written in C.

The library used for retrieving requests to the servers is [socket](https://man7.org/linux/man-pages/man2/socket.2.html) and the library for multithreading is [pthread](https://www.cs.cmu.edu/afs/cs/academic/class/15492-f07/www/pthreads.html).

Examples of how to run the server and load balancer are present within the main commentary of each program. Various flags can be set to specify the number of threads, desired port number and logging option for the HTTP Server, and server addresses must be passed for the Load Balancer.
