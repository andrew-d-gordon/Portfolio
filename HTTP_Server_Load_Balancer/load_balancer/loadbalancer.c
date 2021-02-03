#include<err.h>
#include<arpa/inet.h>
#include<netdb.h>
#include<stdio.h>
#include<stdlib.h>
#include<string.h>
#include<sys/socket.h>
#include<pthread.h>
#include<sys/types.h>
#include<unistd.h>
#include<ctype.h>
#include<stdbool.h>
#include<time.h>
#include<limits.h>

#define INTERNALERRORRESPONSE "HTTP/1.1 500 Internal Server Error\r\nContent-Length: 0\r\n\r\n"

struct bridgeRequestObject { // TO BE USED BY A BRIDGE REQUEST THREAD FOR HANDLING RECV/SEND OPERATIONS

    uint8_t recvline[4097];
    ssize_t recv_bytes;
    fd_set set;
    struct timeval timeout;
    bool is_timedout;
    int fromfd;
    int tofd;

};

struct bridge_request_thread { // STRUCT FOR BRIDGE REQUEST THREAD

    int id;
    pthread_mutex_t* bridge_thread_lock;
    pthread_cond_t* bridge_thread_cond;
    struct bridgeRequestObject bridge_obj;
    int clientsd;
    int serversd;
    pthread_t bridge_req_thread_id;

};

struct optimal_server_finder_thread { // STRUCT FOR OPTIMAL SERVER FINDER THREAD

    // LOCKS AND RELATIVELY CONSTANT VARS TO MAKE SURE WE LOCK CRITICAL SECTIONS BETWEEN DISPATCH AND OPT SERV FINDER THREAD
    pthread_mutex_t* healthcheck_downtime_lock;
    pthread_mutex_t* optimalport_lock;
    pthread_cond_t* requests_condition;
    pthread_t healthCheckerThreadId;
    int flag;
    int Xseconds;

    // VARS FOR FINDING BEST SERVER TO SEND REQUESTS TO
    int current_best_server_port;
    int current_best_server_entries;
    int current_best_server_errors;

    // VARS SHARED BETWEEN DISPATCH AND OPTSERVFINDER THREAD
    int16_t* servers_list;
    int numOfHttpPorts;
    uint16_t* optimal_server_port;
    bool servers_available;

};

/*
 * client_connect takes a port number and establishes a connection as a client.
 * connectport: port number of server to connect to
 * returns: valid socket if successful, -1 otherwise
 */
int client_connect(uint16_t connectport) {
    int connfd;
    struct sockaddr_in servaddr;

    connfd=socket(AF_INET,SOCK_STREAM,0);
    if (connfd < 0)
        return -1;
    memset(&servaddr, 0, sizeof servaddr);

    servaddr.sin_family=AF_INET;
    servaddr.sin_port=htons(connectport);

    /* For this assignment the IP address can be fixed */
    inet_pton(AF_INET,"127.0.0.1",&(servaddr.sin_addr));

    if(connect(connfd,(struct sockaddr *)&servaddr,sizeof(servaddr)) < 0)
        return -1;
    return connfd;
}

/*
 * server_listen takes a port number and creates a socket to listen on 
 * that port.
 * port: the port number to receive connections
 * returns: valid socket if successful, -1 otherwise
 */
int server_listen(int port) {
    int listenfd;
    int enable = 1;
    struct sockaddr_in servaddr;

    listenfd = socket(AF_INET, SOCK_STREAM, 0);
    if (listenfd < 0)
        return -1;
    memset(&servaddr, 0, sizeof servaddr);
    servaddr.sin_family = AF_INET;
    servaddr.sin_addr.s_addr = htonl(INADDR_ANY);
    servaddr.sin_port = htons(port);

    if(setsockopt(listenfd, SOL_SOCKET, SO_REUSEADDR, &enable, sizeof(enable)) < 0)
        return -1;
    if (bind(listenfd, (struct sockaddr*) &servaddr, sizeof servaddr) < 0)
        return -1;
    if (listen(listenfd, 500) < 0)
        return -1;
    return listenfd;
}

/*
 * bridge_connections send up to 100 bytes from fromfd to tofd
 * fromfd, tofd: valid sockets
 * returns: number of bytes sent, 0 if connection closed, -1 on error 
 */
int bridge_connections(int fromfd, int tofd, struct bridgeRequestObject* bridge_obj) { //need recvline to be individual thread buffers, need n or readbytes to be individual to a worker

    memset(&bridge_obj->recvline[0], 0, 4097);
    bridge_obj->recv_bytes = recv(bridge_obj->fromfd, bridge_obj->recvline, 4096, 0);

    if (bridge_obj->recv_bytes < 0) {
        printf("connection error receiving\n");
        return -1;
    } else if (bridge_obj->recv_bytes == 0) { // check case if server crashes in middle of processing request
        printf("receiving connection ended\n");
        return 0;
    }

    bridge_obj->recvline[bridge_obj->recv_bytes] = 0;

    bridge_obj->recv_bytes = send(bridge_obj->tofd, bridge_obj->recvline, bridge_obj->recv_bytes, 0);
    if (bridge_obj->recv_bytes < 0) {
        printf("connection error sending\n");
        return -1;
    } else if (bridge_obj->recv_bytes == 0) {
        printf("sending connection ended\n");
        return 0;
    }
    return bridge_obj->recv_bytes;
}

/*
 * bridge_loop forwards all messages between both sockets until the connection
 * is interrupted. Works with bridge_obj vars from thread that owns it.
 */
void bridge_loop(int sockfd1, int sockfd2, struct bridgeRequestObject* bridge_obj) {

    memset(&bridge_obj->set, 0, sizeof(&bridge_obj->set));
    bridge_obj->timeout.tv_sec = 3;
    bridge_obj->timeout.tv_usec = 0;

    bridge_obj->is_timedout = false;

    while(1) {

        FD_ZERO (&bridge_obj->set);
        FD_SET (sockfd1, &bridge_obj->set); //need sockfd1 and sockfd2 to be unique to threads, also need &set to be unique potentially
        FD_SET (sockfd2, &bridge_obj->set);

        switch (select(FD_SETSIZE, &bridge_obj->set, NULL, NULL, &bridge_obj->timeout)) {
            case -1:
                printf("**ERROR DURING SELECT TO SOCKETS EXITING**\n");
                return;
            case 0:
                bridge_obj->is_timedout = true;
                continue;
            default:
                if (FD_ISSET(sockfd1, &bridge_obj->set)) {
                    bridge_obj->fromfd = sockfd1;
                    bridge_obj->tofd = sockfd2;
                } else if (FD_ISSET(sockfd2, &bridge_obj->set)) {
                    bridge_obj->fromfd = sockfd2;
                    bridge_obj->tofd = sockfd1;
                } else {
                    printf("this should be unreachable in BL\n");
                    return;
                }
        }

        // IF NO MORE RECV/SEND OPERATIONS TO COMPLETE OR WE'VE TIMED OUT, REQUEST HAS BEEN PROCESSED SO RETURN OUT
        if (bridge_connections(bridge_obj->fromfd, bridge_obj->fromfd, bridge_obj) <= 0 || bridge_obj->is_timedout) {
            return;
        }
    }
}

void* bridge_request_worker(void* bridge_thread) {
    struct bridge_request_thread *bridge_req_thread = (struct bridge_request_thread*) bridge_thread;
    memset(&bridge_req_thread->bridge_obj.recvline[0], 0, 4097); // MEMSET OUR BUFFER TO HAVE CLEAN SLATE FOR RECV/SEND OPS
    printf("THREAD SPINNING ID: %d\n", bridge_req_thread->id);

    while(true) {
        while(bridge_req_thread->clientsd < 0) { // WAIT FOR REQUEST TO HANDLE
            int rc = pthread_cond_wait(bridge_req_thread->bridge_thread_cond, bridge_req_thread->bridge_thread_lock);
        }
        bridge_loop(bridge_req_thread->clientsd, bridge_req_thread->serversd, &bridge_req_thread->bridge_obj);
        close(bridge_req_thread->clientsd);
        close(bridge_req_thread->serversd);

        bridge_req_thread->clientsd = INT_MIN; // RESET VALS SO WE CAN SIGNIFY THREAD IS READY FOR ANOTHER REQUEST
        bridge_req_thread->serversd = INT_MIN;
        //printf("%f seconds\n", (double)clock()/CLOCKS_PER_SEC); // current time checker
    }
}

void* optimal_server_checker(void *thread) {
    struct optimal_server_finder_thread *opt_serv_finder = (struct optimal_server_finder_thread*) thread;
    struct timespec ts;
    struct timeval now;

    while (true) {
        
        // SET UP VARS FOR LATER PROCESSING
        uint16_t bestCandidatePort = 0;
        int bestCandidateEntries = INT_MAX;
        int bestCandidateErrors = INT_MAX;

        uint8_t buffer[4096];
        bool entryFound = false;
        int i = 0;

        while(i < opt_serv_finder->numOfHttpPorts) {
            
            opt_serv_finder->flag = 0; // RESET FLAG SO WE DON'T RUN ON SUPRIOUS WAKEUPS LATER ON

            memset(&buffer[0], 0, 4096);
            
            bool responseReceived = false;
            bool responseLeftToReceive = true;

            ssize_t read_bytes;
            uint16_t numOfReceivedBytes = 0;

            int status_code = 0;
            int length = 0;
            int errors = 0;
            int entries = 0;

            // SET UP ATTEMPT TO CONNECT TO SERVER AT PORT NUMBER
            struct timeval timeout;
            struct sockaddr_in server_addr;
            int connfd = socket(AF_INET, SOCK_STREAM, 0);

            if (connfd < 0) {
                return NULL;
            }

            memset(&server_addr, 0, sizeof(server_addr));

            server_addr.sin_family = AF_INET;
            server_addr.sin_port = htons(opt_serv_finder->servers_list[i]);
            inet_pton(AF_INET, "127.0.0.1", &(server_addr.sin_addr));
            if (connect(connfd, (struct sockaddr *)&server_addr, sizeof(server_addr)) < 0) {
                printf("**ERROR CONNECTING IN OPTSERVFINDER, SERVER NOT UP**\n");
                responseLeftToReceive = false;
            }

            fd_set set;
            FD_ZERO (&set);
            FD_SET (connfd, &set);

            timeout.tv_sec = 3; // TIMEOUT AFTER THIS AMOUNT OF TIME IN SELECT FOR RECEIVING RESPONSE FROM SERVER IF VALID SERVER
            timeout.tv_usec = 0;

            if(responseLeftToReceive) { // IF WE HAVE A VALID CONNECTION, SEND A HEALTHCHECK REQUEST
                int ret = dprintf(connfd, "GET /healthcheck HTTP/1.1\r\n\r\n");
                if (ret < 0) {
                    return NULL;
                }
            }

            while(responseLeftToReceive) { // ATTEMPT TO READ RESPONSE FROM SERVER INTO THE BUFFER FROM SOCKET
                switch (select(FD_SETSIZE, &set, NULL, NULL, &timeout)) {
                    case -1:
                        printf("**SELECT ERROR TO SERVER IN OPTSERVERFINDER**\n");
                        status_code = 500;
                        responseReceived = false;
                        responseLeftToReceive = false;
                        break;
                    case 0:
                        printf("<SELECT TIMED OUT IN OPTSERVERFINDER>\n");
                        responseLeftToReceive = false;
                        break;
                    default:
                        if (FD_ISSET(connfd, &set)) {
                            responseReceived = true;
                            read_bytes=recv(connfd, buffer+numOfReceivedBytes, 4096-numOfReceivedBytes, 0);
                            if(read_bytes == 0) {
                                responseLeftToReceive = false;
                                break;
                            }
                            numOfReceivedBytes = numOfReceivedBytes + read_bytes;
                            buffer[numOfReceivedBytes] = 0;
                        } else {
                            printf("<SHOULD BE UNREACHABLE IN OPTSERVERFINDER\n");
                            status_code = 500;
                            responseReceived = false;
                            responseLeftToReceive = false;
                            break;
                        }
                }
            }

            if(responseReceived) {
                int nscan = sscanf(buffer, "HTTP/1.1 %d OK\r\nContent-Length: %d\r\n%d\n%d", &status_code, &length, &errors, &entries);
            }

            if(status_code != 200 || !(responseReceived)) { // PROCESS RESEPONSE FROM SERVER ON HEALTHCHECK IS WE RECVD RESPONSE
                printf("**SERVER DOES NOT HAVE LOGGING ENABLED OR ERRORED IN OPTSERVERFINDER**\n");
            } else {
                entryFound = true; // NOTIFY WE HAVE A SERVER THAT CAN HANDLE PROCESSING
                if(entries < bestCandidateEntries) { // NEW ENTRIES SEEN IS LESS THAN CURRENT MIN, UPDATE CURRENT MIN VALUES + OPTIMAL PORT CANDIDATE
                    bestCandidateEntries = entries;
                    bestCandidateErrors = errors;
                    bestCandidatePort = opt_serv_finder->servers_list[i];
                } else if (entries == bestCandidateEntries) { // NEW ENTRIES SEEN IS EQUAL TO CURRENT MIN AND IF NEW FAILS LESS THAN CURRENT, UPDATE CURRENT MIN VALUES + OPTIMAL PORT CANDIDATE
                    if(errors > bestCandidateErrors) {
                        bestCandidateEntries = entries;
                        bestCandidateErrors = errors;
                        bestCandidatePort = opt_serv_finder->servers_list[i];
                    }
                }
            }

            // INCREMENT WHICH INDEX TO LOOK AT PORT NUMBERS
            i=i+1;
            close(connfd);
        }

        pthread_mutex_lock(opt_serv_finder->optimalport_lock);
        if(entryFound) {
            *opt_serv_finder->optimal_server_port = bestCandidatePort; // SET BEST PORT
            opt_serv_finder->servers_available = true; // ACKNOWLEDGE A SERVER IS AVAILABLE TO PROCESS
        } else { //NO SERVERS AVAILABLE
            opt_serv_finder->servers_available = false;
        }
        pthread_mutex_unlock(opt_serv_finder->optimalport_lock);

        int cond_timedwait_return = -1; // WILL HOLD RETURN OF CONDTIMEDWAIT, 
        pthread_mutex_lock(opt_serv_finder->healthcheck_downtime_lock);
        
        memset(&ts, 0, sizeof(ts));
        gettimeofday(&now, NULL);
        ts.tv_sec = now.tv_sec + opt_serv_finder->Xseconds; // TIMEOUT THIS WAIT AFTER X AMOUNT OF SECONDS SPECIFIED IN MAIN
        //IF RETRUN ON CONDTIMEDWAIT == 0, SPURIOUS OR SIGNALLED WAKEUP, NEED FLAG TO MAKE SURE IT WAS SIGNALLED, IF >0 TIMEOUT OCCURED SO WE CAN BREAK
        while(!(cond_timedwait_return==0 && opt_serv_finder->flag) && cond_timedwait_return <= 0) { 
            cond_timedwait_return = pthread_cond_timedwait(opt_serv_finder->requests_condition, opt_serv_finder->healthcheck_downtime_lock, &ts);
        }
        if (opt_serv_finder->flag) {
            pthread_mutex_unlock(opt_serv_finder->healthcheck_downtime_lock);
        }
        pthread_mutex_unlock(opt_serv_finder->healthcheck_downtime_lock);
    }
    return NULL;
}

int main(int argc, char **argv) {

    if (argc < 3) { // NOT ENOUGH ARGS TO RUN LOAD BALANCER
        printf("missing arguments: usage %s port_to_connect port_to_listen", argv[0]);
        return 1;
    }

    uint8_t secondsBeforeOptimalCheck = 4; // X SECONDS TO TIMEOUT AND RUN OPTIMAL SERVER CHECK
    int concurrentRequests = 4; // DEFAULT NUMBER OF CONCURRENT REQUESTS TO SERVER
    int numOfRequestsPreOpt = 5; // DEFAULT NUMBER OF REQUESTS BEFORE NEW RUN OF FINDING OPTIMAL SERVER
    int flagargs = 0; // HELPS DETERMINE HOW MANY PROGRAM ARGS ARE TIED WITH FLAG ARGS, HELPS SPECIFY HOW MANY PORT NUMBERS ARE AVAILABLE
    char* LBport = NULL; // WILL HOLD LOADBALANCER PORT WHICH WE WILL LISTEN ON
    size_t requests_counter = 0; // REQUESTS COUNTER FOR DISPATCH TO SIGNAL HEALTHCHECK WHEN numOfRequestsPreOpt THRESHOLD REACHED
    bool servers_available = false; // BOOLEAN TO HELP SIGNIFY IF WE FOUND ANY SERVERS TO PROCESS REQUESTS
    int connfd, listenfd, acceptfd; // LISTEN IS LB PORT SOCKET, CONN FOR SERVER TO PROCESS REQUEST, ACCEPT FOR CLIENT REQUEST
    uint16_t connectport, listenport; // OPTIMAL SERVER PORT TO CONNECT TO, PORT TO LISTEN ON 
    connectport = 100; // SET CONNECTPORT TO DUMMY VALUE WHICH WILL BE ALTERED BY OPT SERV FINDER THREAD OR BE SET TO INVALID
    
    int is_error = 0; // TO HOST VALUE OF PTHREAD_CREATE OPERATION LOWER
    int c; // WILL HOST CHAR FROM GET OPT
    while ((c = getopt(argc, argv, ":N:R:")) != -1) { // PARSE PROGRAM ARGUMENTS
        switch (c) {
            case 'N':
                if (strncmp(optarg, "-N", strlen("-N")) == 0 || (atoi(optarg) < 1)) {
                    fprintf(stderr, "-N needs a valid argument\n");
                    return EXIT_FAILURE;
                }
                concurrentRequests = atoi(optarg);
                flagargs++;
                break;
            case 'R':
                if (strncmp(optarg, "-N", strlen("-N")) == 0 || (atoi(optarg) < 1)) {
                    fprintf(stderr, "-R needs a valid argument\n");
                    return EXIT_FAILURE;
                } else {
                    numOfRequestsPreOpt = atoi(optarg);
                    flagargs++;
                    break;
                }
            case '?':
                if (optopt == 'c') {
                    fprintf(stderr, "Option -%c requires an argument.\n", optopt);
                } else if (isprint (optopt)) { // SEEING IF OPTOPT IS A PRINTABLE CHARACTER
                    fprintf(stderr, "Unknown option -%c.\n", optopt);
                } else {
                    fprintf(stderr, "Unknown option character \\x%x'.\n", optopt);
                }
                return EXIT_FAILURE;
            default:
                abort();
        }
    }

    if (optind >= argc) {
        fprintf(stderr, "ERR: PORT NUMBER REQUIRED TO START SERVER\n");
        return EXIT_FAILURE;
    }
    
    int numOfHttpPorts = argc-((flagargs*2)+2);
    int16_t servers_list[numOfHttpPorts];

    LBport = argv[optind];
    optind++;
    printf("lbport: %s\n", LBport);
    
    int i = 0;
    while(optind < argc) { // PROCESS AND VALIDATE (NEEDS TO BE POSITIVE) PORT NUMBERS PASSED IN PROG. ARGS
        if(atoi(argv[optind]) < 0) {
            fprintf(stderr, "Port number arguments be positive\n");
            return EXIT_FAILURE;
        }
        servers_list[i] = atoi(argv[optind++]);
        printf("portnumbers index %d: %d\n", i, servers_list[i]);
        i++;
    }

    listenport = atoi(LBport); // SET UP LISTENING PORT TO RECV CONNECTIONS ON
    if ((listenfd = server_listen(listenport)) < 0)
        err(1, "failed listening");

    // INITILAIZE OPTIMAL SERVER FINDER (HEALTHCHECKING) THREAD VALS AND START THREAD FUNC
    pthread_mutex_t healthcheck_downtime_lock = PTHREAD_MUTEX_INITIALIZER;
    pthread_mutex_t connectport_lock = PTHREAD_MUTEX_INITIALIZER;
    pthread_cond_t requests_cond_var = PTHREAD_COND_INITIALIZER;
    
    struct optimal_server_finder_thread optimalServerChecker;
    optimalServerChecker.flag = 0;
    optimalServerChecker.healthcheck_downtime_lock = &healthcheck_downtime_lock;
    optimalServerChecker.optimalport_lock = &connectport_lock;
    optimalServerChecker.requests_condition = &requests_cond_var;
    optimalServerChecker.numOfHttpPorts = numOfHttpPorts;
    optimalServerChecker.optimal_server_port = &connectport; //needs to be pointer int
    optimalServerChecker.servers_list = servers_list; // these three probably should run at the beginning and be ints, maybe just cast failed/total to double when needed
    optimalServerChecker.servers_available = servers_available; 
    optimalServerChecker.Xseconds = secondsBeforeOptimalCheck; // SETTING NUMBER OF SECONDS BEFORE TIMEOUT!
    is_error = pthread_create(&optimalServerChecker.healthCheckerThreadId, NULL, optimal_server_checker, (void *)&optimalServerChecker);
    if (is_error) { // PROBLEM STARTING OPTIMAL SERVER CHECKING THREAD
        return EXIT_FAILURE;
    }
    
    // INITILAIZE BRIDGE_REQUEST_THREAD(s) VALS AND START THREAD(s) FUNCTIONS
    pthread_mutex_t bridge_threads_lock = PTHREAD_MUTEX_INITIALIZER;
    pthread_cond_t bridge_thread_conditional = PTHREAD_COND_INITIALIZER;
    struct bridge_request_thread bridge_request_threads[concurrentRequests]; // concurrent requests handler
    is_error = 0;
    for (int j = 0; j < concurrentRequests; j++) {
        bridge_request_threads[j].serversd = INT_MIN;
        bridge_request_threads[j].clientsd = INT_MIN;
        bridge_request_threads[j].id = j;
        bridge_request_threads[j].bridge_thread_cond = &bridge_thread_conditional;
        bridge_request_threads[j].bridge_thread_lock = &bridge_threads_lock;
        
        is_error = pthread_create(&bridge_request_threads[j].bridge_req_thread_id, NULL, bridge_request_worker, (void *)&bridge_request_threads[j]);
        if (is_error) {
            return EXIT_FAILURE;
        }
    }

    // VARS TO HELP FIND DESIRED BRIDGE_REQUEST_THREAD TO PROCESS REQUEST
    int target_bridge_thread = 0; 
    int target_bridge_thread_looper = 0;
    usleep(1000); // SHORT USLEEP TO MAKE SURE OPT SERVER FINDER THREAD HAS CHANCE TO RUN...
    while(1) {
        if ((acceptfd = accept(listenfd, NULL, NULL)) < 0) // ACCEPT REQUEST
            err(1, "failed accepting");

        requests_counter++;
        if(requests_counter%numOfRequestsPreOpt == 0) { // IF -R NUMBER OF REQUESTS HAVE BEEN PROCESSED, ATTEMPT TO SIGNAL OPTSERVFINDER THREAD TO BEGIN NEW CHECK
            pthread_mutex_lock(optimalServerChecker.healthcheck_downtime_lock);
            printf("<SIGNAL HEALTH CHECKS ON SERV, REQUEST# REACHED>\n");
            optimalServerChecker.flag = 1;
            pthread_cond_broadcast(optimalServerChecker.requests_condition);
            pthread_mutex_unlock(optimalServerChecker.healthcheck_downtime_lock);
            requests_counter = 0;
        }

        pthread_mutex_lock(optimalServerChecker.optimalport_lock);
        if(!(optimalServerChecker.servers_available)) { // NO SERVERS WERE FOUND IN OPTSERVFINDER THREAD, SEND 500 AND CONTINUE
            printf("**ERROR CONNECTING IN DISPATCH, NO SERVS AVAILABLE**\n");
            send(acceptfd, INTERNALERRORRESPONSE, strlen(INTERNALERRORRESPONSE), 0);
            pthread_mutex_unlock(optimalServerChecker.optimalport_lock);
            close(acceptfd);
        } else {
            //connectport = servers_list[j%numOfHttpPorts];
            if ((connfd = client_connect(connectport)) < 0) { // CANNOT CONNECT TO SERVER AT SPECIFIED PORT, SEND 500 AND CONTINUE
                printf("**ERROR CONNECTING IN DISPATCH, SERVER ON CONNECTPORT UNAVAILABLE**\n");
                send(acceptfd, INTERNALERRORRESPONSE, strlen(INTERNALERRORRESPONSE), 0);
                pthread_mutex_unlock(optimalServerChecker.optimalport_lock);
                close(acceptfd);
            } else {
                pthread_mutex_unlock(optimalServerChecker.optimalport_lock);
                printf("==STARTING BRIDGING OF REQUESTS==\n");
                while(1) { // LOOK FOR READY THREAD, BROADCAST IF FOUND, ELSE USLEEP .1S AND LOOK AGAIN
                    target_bridge_thread = target_bridge_thread_looper%concurrentRequests;
                    if(bridge_request_threads[target_bridge_thread].clientsd < 0) { // IF THREAD IS READY TO PROCESS A REQUEST, PROVIDE THEM THE WORK AND BROADCAST TO GO
                        bridge_request_threads[target_bridge_thread].clientsd = connfd;
                        bridge_request_threads[target_bridge_thread].serversd = acceptfd;
                        pthread_cond_broadcast(bridge_request_threads[target_bridge_thread].bridge_thread_cond);
                        break;
                    }
                    usleep(1000);
                    target_bridge_thread_looper++;
                }
            }
        }
    }
    return EXIT_SUCCESS;
}