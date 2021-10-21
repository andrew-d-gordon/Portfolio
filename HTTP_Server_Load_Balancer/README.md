# Threaded HTTP Server and Load Balancer

This project contains an HTTP Server utilizing multithreading and a respective Load Balancer, each written in C.
The library used for retrieving requests to the servers is 'socket' and the library for multithreading is 'pthread'.

Examples of how to run the server and load balancer are present within the main commentary of each program. Various flags can be set to specify the number of threads, desired port and logging for the HTTP Server and server addresses must be passed for the load balancer.
