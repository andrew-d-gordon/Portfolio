#include <sys/socket.h>
#include <errno.h>
#include <sys/stat.h>
#include <sys/ioctl.h>
#include <poll.h>
#include <stdio.h>
#include <netinet/in.h>
#include <netinet/ip.h>
#include <pthread.h>
#include <fcntl.h>
#include <unistd.h> // write
#include <string.h> // memset
#include <stdlib.h> // atoi
#include <stdbool.h> // true, false
#include <limits.h> // int_min
#include <ctype.h>
#include <time.h>

#define MAX9DIGDEC 100000000
#define BUFFER_SIZE 6145
#define CONVERTED_BUFFER_SIZE 4141 //2071 //or 2761
#define FILE_BYTES_PER_CONV_BUFF 1200
#define FourKibibytes 4096
#define BYTESPERLOGLINE 20
#define HEALTHCHECKSTR "healthcheck"
#define CONTENTLENGTHSTR "Content-Length"
#define FILENAMESTR "/"
#define HTTPVERSTR "HTTP/1.1\r\n"
#define PUTSTR "PUT"
#define GETSTR "GET"
#define HEADSTR "HEAD"
#define HEADERSTARTS "\r\n"
#define BODYSTARTSTR "\r\n\r\n"
#define RESPONSEBASE "HTTP/1.1 sc# \r\nContent-Length: \r\n\r\n"
#define LOGRESPONSECLOSE "========\n"
#define LOGRESPONSEHEADERBASE "FAIL:  / length 32 --- response sc#\n"

/* This httpserver's primary goal was to process PUT, HEAD, and GET requests concurrently as well as have the ability to log responses
which were sent back to the client. When booted the server must be supplied a port number and can be supplied with -l and -N flags (in any order).
The -l flag is used to notify the server to log responses and pertinent data (in the case of PUT/GET) to a specified log file name after
the flag (can already exist or not, if permitted existing files will be truncated).
The -N flag is used to specify how many threads you would like the server to spin. If none specified the default spun is 4.
At the moment there is some rudimentary Mutex locks being used around critical regions and some busy waiting where the dispatcher thread
supplies workers with requests to fulfill. These aspects will be tuned up more in the recent future to be less prone to scheduling issues
and more efficient.
(Also as a quirk of our intitial assignment I have added the functionality to effectively hexdump the contents of a GET/PUT request
to the log file. This functionality can be bypassed by removing the calls to the writeHexBodyToLog function as well as setting 
bodyResponseSize to 0 in the log_response function.)*/

struct httpObject { // USED TO KEEP TRACK OF ALL INFO HTTP REQUEST INFORMATION

    // GENERAL USE
    char method[200];                               // PUT, HEAD, GET
    char filename[255];                             // what is the file we are worried about
    char httpversion[9];                            // HTTP/1.1
    char status_code_string[22];                    // status code string to put in response to client
    uint8_t buffer[BUFFER_SIZE];                    // buffer for general use due to space limitations
    int16_t filefd;
    char *responseHeader;                           // will store response header to send to client
    ssize_t content_length;                         // content length of file req/PUT
    int status_code;                                // holder for status code integer values
    bool is_val_msg;                                // valid message boolean
    uint8_t numberStrSize;
    ssize_t numCopy;

    // READ HTTP RESPONSE/PROCESSING REQUEST
    uint8_t headerStarts[4097];                     // buffer to parse through headers, at end saves body contents in header
    char headString1[513];                          // String to hold stringFinder contents (boosts concurrency so multiple threads can check for CONTENT-LEN)
    bool cl_wanted;                                 // set to true if content length is wanted
    bool cl_written;                                // set to true if content length has been written
    bool is_body_in_header;                         // boolean to see if we have body contents in header
    bool do_send_File_Body;                         // boolean to see if we want to send the file body from get
    bool firstHeader;
    int8_t pollReturn;
    size_t writeToDestinationOffset;                // primarily for PUT'ing to file
    ssize_t numOfReceivedBytes;
    ssize_t currDBytesWritten;                      // keeps written bytes to destination in CFSTD
    ssize_t read_bytes;
    ssize_t bytesLeftToWrite;
    int16_t bytesAfterHeaderCount;
    int8_t numberScanned;
    struct stat statbufF;
    struct pollfd socketIOcheck;
    
    
    // LOGGING SPECIFIC (HEALTHCHECK AS WELL)
    char convertedFileBody[CONVERTED_BUFFER_SIZE];  // to hold converted body lines from files read
    size_t bodyResponseSize;
    size_t responseStrSize;
    size_t responseHeadStrSize;
    int16_t currTotalLogs;
    int16_t currFailedLogs;
    size_t bytesToConvertInLine;                    // will be val of how many bytes to convert for a given line (<=20)
    size_t bytes_converted_from_buffer;             // num of bytes converted from buf in a given read
    size_t total_bytes_written_to_log;
    size_t bytesConvertedInLine;
    size_t bytefoldover; 
    size_t bytesReadInLine;
    ssize_t currLBytesWritten;                       // keeps log bytes written to log in WHXL
    ssize_t total_file_bytes_seen;
    ssize_t logContentLength;
    size_t currLogOffset;
    ssize_t cfstdOffset;
    bool do_want_healthcheck;                       // signifies we want to do healthcheck
    bool log_is_live;                               // signifies whether we are logging responses
    bool want_body_in_log;
    
};

struct logObject { // USED TO KEEP TRACK OF ALL INFO FOR LOGFILE INFORMATION

    char logfilename[256];
    int logfd;
    uint16_t failed_logs;
    uint16_t total_logs;
    bool want_response_log;
    ssize_t logSizeOffset;

};


/*
stringFinder will server to find denoted strings from given locations, with given structures (str_sequence input), and set the values to the appropriate destinations (httpobj message attributes).
*/
int8_t stringFinder(char *str_key, char *source_str, char location_str_dest[4097], char *str_sequence, void* destination, void *destination2) { //desired length int8_t
    char* str_location;
    int8_t numscan = -1;
    if((str_location = strstr(source_str, str_key))) { // see if HEAD method requested
        if(destination2==NULL) { //one argument case (for method/filename/httpver/CL val checking)
            numscan = sscanf(str_location, str_sequence, destination);
        } else { // two destination case (for header checking)
            numscan = sscanf(str_location, str_sequence, destination, destination2);
        }

        if(location_str_dest != NULL) { // if we want to store the string found from the strstr on source_str w/delimiter str_key
            memmove(location_str_dest, str_location, strlen(str_location));
            location_str_dest[strlen(str_location)] = '\0';
        }
    }
    return numscan;
}

/*
    \brief 1. Want to read in the HTTP message/ data coming in from socket
    \param client_sockd - socket file descriptor
    \param message - object we want to 'fill in' as we read in the HTTP message
*/

void read_http_response(ssize_t client_sockd, struct httpObject* message, pthread_mutex_t* stringFinderLock) {
    //RECV UP TO FOUR KIB OF DATA FROM SOCKET, PARSE DATA TO AND CALL STRINGFINDER TO SEE IF DESIRED STRINGS EXIST OR IF INVALID FORMATTING EXISTS

    message->socketIOcheck.events = POLLIN;
    message->socketIOcheck.fd = client_sockd;
    
    while(message->numOfReceivedBytes < FourKibibytes) { // ATTEMPT TO READ 4 KiB INTO THE BUFFER FROM SOCKET, INFO COULD BE PART OF HEAD OR BODY, BEGIN TO PARSE ON POLL TIMEOUT
        message->pollReturn = poll(&message->socketIOcheck, 1, 1000); // POLL SOCKET WITH .1 SECOND TIMEOUT
        if(message->pollReturn > 0) { // POLL SIGNALS SOCKET IS READY FOR I/O OPERATIONS
            message->read_bytes=recv(client_sockd, message->buffer+message->numOfReceivedBytes, FourKibibytes-message->numOfReceivedBytes, 0);
            message->numOfReceivedBytes = message->numOfReceivedBytes + message->read_bytes;
            message->buffer[message->numOfReceivedBytes] = 0;
        } else if (message->pollReturn == 0) { // POLL TIMED OUT, CARRY ON WITH DATA RECV'D
            break;
        } else { // POLL ERRORED
            message->is_val_msg = false;
            message->status_code = 500;
            return;
        }
    }

    sscanf((char *) &message->buffer, "%s ", message->method);

    if(strncmp(message->method, PUTSTR, strlen(PUTSTR)) == 0) {
        message->cl_wanted = true;
    }

    // LOCK
    pthread_mutex_lock(stringFinderLock);
    stringFinder(FILENAMESTR, (char*) &message->buffer, NULL, "/%s ", message->filename, NULL); // FIND FILENAME

    stringFinder(HTTPVERSTR, (char*) &message->buffer, NULL, "%[^\r\n]s", message->httpversion, NULL); // FIND HTTPVER
    pthread_mutex_unlock(stringFinderLock);
    // UNLOCK

    char headString2[513];
    
    while (1) { // ATTEMPT TO PARSE ALL AVAILABLE HEADERS, SIGNAL IF BAD HEADER, IF DOUBLE CLRF SEEN, CHECK IF IT'S THE END OR SOME BODY DATA IS AVAILABLE TO READ
        
        //LOCK
        pthread_mutex_lock(stringFinderLock);
        // FIRST HEADER FIND IS RUN OFF OF ENTIRE BUFFER, STORES STR FROM FIRST HEADER TO HEADERSTARTS, SUBSEQUENT RUN ON HEADERSTARTS+2
        if(message->firstHeader) {
            message->numberScanned = stringFinder(HEADERSTARTS, (char*) &message->buffer, (char *) &message->headerStarts, "\r\n%[^:\r\n]: %[^\r\n]%*[\r\n]", message->headString1, &headString2);
            message->firstHeader = false;
        } else {
            message->numberScanned = stringFinder(HEADERSTARTS, (char *) &message->headerStarts+strlen(HEADERSTARTS), (char *) &message->headerStarts, "\r\n%[^:\r\n]: %[^\r\n]%*[\r\n]", message->headString1, &headString2);
        }
        pthread_mutex_unlock(stringFinderLock);
        //UNLOCK

        if(message->numberScanned == 2) { // VALID HEADER, IF WE WANT CONTENT LEN AND IT'S CONTENT LEN HEADER, STORE CONTENT LEN, CONTINUE
            if(strncmp(message->headString1, CONTENTLENGTHSTR, strlen(CONTENTLENGTHSTR)) == 0 && !(message->cl_written) && message->cl_wanted) {
                pthread_mutex_lock(stringFinderLock);
                stringFinder(CONTENTLENGTHSTR, (char *) &message->headerStarts+strlen(HEADERSTARTS), NULL, "Content-Length: %zd", &message->content_length, NULL);
                pthread_mutex_unlock(stringFinderLock);
                message->cl_written = true;
            }
        } else { // STR DOES NOT CONFORM TO HEADER FORMAT, IF 2XCLRF AND BODY DATA EXISTS, READ BODY TO BUF THEN BREAK, ELSE SIGNAL BAD REQUEST
            if(strncmp(BODYSTARTSTR, (char *) &message->headerStarts, strlen(BODYSTARTSTR)) == 0) { // reached end of headers, break
                message->bytesAfterHeaderCount = message->numOfReceivedBytes - (strlen((char *)&message->buffer) - strlen((char *)&message->headerStarts + strlen(BODYSTARTSTR)));
                if((message->bytesAfterHeaderCount != 0) && message->cl_written && message->cl_wanted) {
                    memmove(message->headerStarts, (uint8_t*)message->buffer+(strlen((char *)&message->buffer) - strlen((char *)&message->headerStarts + strlen(BODYSTARTSTR))), message->bytesAfterHeaderCount);
                    message->is_body_in_header = true;
                }
                break;
            } else {
                message->is_val_msg = false;
                message->status_code = 400;
                break;
            }
        }
    }
    return;
}

void writeHexBodyToLog(struct httpObject* message, struct logObject* log, ssize_t content_length) {

    message->bytes_converted_from_buffer = 0;
    memset(&message->convertedFileBody[0], 0, sizeof(message->convertedFileBody));
    while (message->bytes_converted_from_buffer < (BUFFER_SIZE-145) && message->total_bytes_written_to_log < message->bodyResponseSize) { // CONVERT ALL BYTES IN BUFFER TO HEX VALUES, 

        message->bytesConvertedInLine = 0; // RESET VAL OF OFFSET FOR CONVERTEDBODYLINE IN SNPRINTF
        message->bytesReadInLine = 0;

        message->bytesToConvertInLine = FILE_BYTES_PER_CONV_BUFF; 
        if(message->total_file_bytes_seen > (content_length - FILE_BYTES_PER_CONV_BUFF)) { message->bytesToConvertInLine = content_length - message->total_file_bytes_seen;} // IF LESS THAN BYTESPERLOGLINE LEFT TO CONVERT, ONLY CONVERT REMAINDER
        
        while (message->bytesReadInLine < message->bytesToConvertInLine) { // THIS LOOP WILL SERVE TO CONVERT message->bytesToConvertInLine BYTES OF DATA IN THE BUFFER TO A STRING WHICH WILL WRITTEN TO OUR LOG FILE AT INCREASING OFFSET
            
            if(message->bytesReadInLine % BYTESPERLOGLINE == 0) { // PRINT BEGINNING OF NEW LINE SEQUENCE
                message->bytesConvertedInLine += snprintf(message->convertedFileBody + message->bytesConvertedInLine, 10, "%08zd ", message->total_file_bytes_seen - (MAX9DIGDEC*message->bytefoldover)); // 9 BYTES OF CONVERTED LINE TO BE $08d (reset after 9 digits reached)
            }
            
            if (message->bytesReadInLine % BYTESPERLOGLINE != (BYTESPERLOGLINE-1) && message->bytesReadInLine < message->bytesToConvertInLine-1) { // PRINT CONVERTED CHAR
                message->bytesConvertedInLine += snprintf(message->convertedFileBody + message->bytesConvertedInLine, 4, "%02x ", message->buffer[message->bytes_converted_from_buffer]);
            } else { // END OF CONVERTED LINE CHAR
                message->bytesConvertedInLine += snprintf(message->convertedFileBody + message->bytesConvertedInLine, 4, "%02x\n", message->buffer[message->bytes_converted_from_buffer]);
            }

            message->bytesReadInLine++;
            message->bytes_converted_from_buffer++;
            message->total_file_bytes_seen++;
        }

        message->currLBytesWritten = pwrite(log->logfd, message->convertedFileBody, strlen(message->convertedFileBody), message->currLogOffset); // WRITE CONVERTEDBODYLINE TO LOG_FILE AT OFFSET
        message->currLogOffset += message->currLBytesWritten; // UPDATE OFFSET
        message->total_bytes_written_to_log += message->currLBytesWritten;

        if(message->total_file_bytes_seen % MAX9DIGDEC == 0) { // USE FOLDEROVER COUNT TO WRAP VALUES BACK TO ZERO AFTER 99999999 BYTES CONVERTED
            message->bytefoldover++;
        }
    }
    
    //message->total_bytes_written_to_log+=message->currLBytesWritten;
    return;
}

/* THIS WILL HANDLE COPYING FROM SOURCE TO DESTINATION AND SENDING BODY CONTENTS TO LOG IN THE CASE OF A PUT OR GET */
void copyFromSourceToDest(int8_t source, ssize_t offset, int8_t destination, struct httpObject* message, struct logObject* log) { //copyFileToStdout copies the contents of the requested source to standard out
    
    message->total_file_bytes_seen = 0;
    message->numOfReceivedBytes = message->bytesAfterHeaderCount;
    message->read_bytes = message->bytesAfterHeaderCount;
    message->writeToDestinationOffset = offset;

    if(message->numOfReceivedBytes == message->content_length) {
        write(destination, message->buffer, message->numOfReceivedBytes);
        writeHexBodyToLog(message, log, message->content_length);
    }

    while(message->numOfReceivedBytes < message->content_length) { // attempt to read content_length amount of bytes into buf from the source, stop when no more bytes can be read or if error occurs

        message->pollReturn = poll(&message->socketIOcheck, 1, 1000); // CHECK SOURCE FOR I/O READINESS, RETURN IF TIMEOUT/ERR OCCURS
        if(message->pollReturn == 0 || message->pollReturn == -1) { 
            return;
        }

        message->read_bytes = message->read_bytes + read(source, message->buffer+message->bytesAfterHeaderCount, (BUFFER_SIZE-145)-message->bytesAfterHeaderCount);
        message->buffer[message->read_bytes] = 0;

        if(message->read_bytes < 0) { // READ ON SOURCE FAILED
            return;
        }

        if(log->want_response_log) {
            message->is_body_in_header = false;
            writeHexBodyToLog(message, log, message->content_length);
        }

        message->currDBytesWritten = write(destination, message->buffer, message->read_bytes);

        if(message->currDBytesWritten < 0) { // our call to write to destination failed, set status code to 500
            return;
        }
        
        message->numOfReceivedBytes += message->read_bytes - message->bytesAfterHeaderCount;
        //printf("what is numOfReceivedBytes CFSTD: %zd\n", message->numOfReceivedBytes);

        while(message->currDBytesWritten > 0 && message->currDBytesWritten < message->read_bytes) { // WHEN MOST RECENT WRITE DOES NOT WRITE AS MANY BYTES AS WERE READ, KEEP TRYING TO WRITE SAID UNWRITTEN BYTES
            message->bytesLeftToWrite = message->read_bytes-message->currDBytesWritten;
            message->currDBytesWritten = message->currDBytesWritten + write(destination, message->buffer+message->currDBytesWritten, message->bytesLeftToWrite);
            if((message->read_bytes-message->currDBytesWritten) < message->bytesLeftToWrite) { // IF WRITE STARTS FAILING, JUST RETURN OUT
                return;
            }
        }
        message->read_bytes = 0;
        message->bytesAfterHeaderCount = 0;

    }

    return;
}

void PUT(struct httpObject* message) {
    // VALIDATE PERMISSIONS OF FILE, THEN CALL TO WRITE BODY DATA TO FILE
    stat(message->filename, &message->statbufF);

    if(access(message->filename, F_OK) > -1) { // ENTITY EXISTS WITH NAME
        if (!(message->statbufF.st_mode & S_IWUSR)) { // FORBIDDEN, ENTITY EXISTS WITH SAME NAME BUT IS NOT A FILE/FILE CANNOT BE WRITTEN TO
            message->status_code = 403;
            message->is_val_msg = false;
            return;
        }

        if ((message->statbufF.st_mode & S_IFMT) != S_IFREG) { // forbidden request check, entity w/filename not a file type
            message->status_code = 403; 
            message->is_val_msg = false;
            return;
        }
    }

    message->filefd = open(message->filename, O_CREAT | O_WRONLY | O_TRUNC, 0644);
    if (message->filefd == -1) { // FILE COULD NOT BE OPENED/CREATED WITH THESE PERMISSIONS
        message->status_code = 403; 
        message->is_val_msg = false;
        return;
    }

    message->status_code = 201; // FILE CAN BE WRITTEN TO, SET STATUS TO 201 FOR CREATED
    
    return;
}

void GET_or_HEAD(struct httpObject* message) {
    // VALIDATE PERMISSIONS OF FILE, IF GET FLAG THAT WE WANT BODY DATA AFTER RESPONSE

    message->filefd = open(message->filename, O_RDONLY);

    if(access(message->filename, F_OK) == -1) { // NO FILE EXISTS WITH THIS NAME
        message->status_code = 404; 
        message->is_val_msg = false;
        return;
    }

    stat(message->filename, &message->statbufF);
    if (!(message->statbufF.st_mode & S_IRUSR)) { // ENTITY WITH THIS NAME IS NOT A FILE/FILE CANNOT BE READ
        message->status_code = 403; 
        message->is_val_msg = false;
        return;
    }

    if ((message->statbufF.st_mode & S_IFMT) != S_IFREG) { // ENTITY WITH FILENAME NOT A FILE
        message->status_code = 403; 
        message->is_val_msg = false;
        return;
    }
    
    if (message->filefd == -1) { // FILE COULD NOT BE OPENED WITH REQUESTED PERMISSIONS
        message->status_code = 403;
        message->is_val_msg = false;
        return;
    }

    fstat(message->filefd, &message->statbufF); // SET CONTENT LENGTH TO SIZE OF FILE REQUESTED

    message->content_length = message->statbufF.st_size;
    message->status_code = 200; // SET STATUS TO 200 FOR OK
    return;
}

/*
    Determine status_code of HTTP request from socket, store values into status_code and status_code_msg for response
*/
void status_code_str(int status_code, char status_code_string[22]) {
    if(status_code == 200) {
        strncpy(status_code_string, "OK", strlen("OK")+1);
    } else if (status_code == 201) {
        strncpy(status_code_string, "Created", strlen("Created")+1);
    } else if (status_code == 400) {
        strncpy(status_code_string, "Bad Request", strlen("Bad Request")+1);
    } else if (status_code == 403) {
        strncpy(status_code_string, "Forbidden", strlen("Forbidden")+1);
    } else if (status_code == 404) {
        strncpy(status_code_string, "Not Found", strlen("Not Found")+1);
    } else {
        strncpy(status_code_string, "Internal Server Error", strlen("Internal Server Error")+1);
    }
    return;
}

int8_t lengthOfIntegerString(ssize_t number, struct httpObject* message) { // FIND LENGTH OF INTEGER AS STR, NUMSTRSIZE STARTS AT 1
    message->numberStrSize = 1;
    message->numCopy = number;
    if(message->numCopy != 0) {
        while (message->numCopy >= 10) { // TAKING LOGS OF VALUE IN CONTENT LENGTH AND INCREMENT HOW LONG CL AS STR WILL BE
            message->numberStrSize = message->numberStrSize+1;
            message->numCopy = message->numCopy / 10;
        }
    }
    return message->numberStrSize;
}

/*
    GENERATE LOG HEADER IF LOG IS LIVE, RESERVE SPACE IF WE HAD A PUT OR GET RESP
*/
void log_response(struct httpObject* message, struct logObject* log, pthread_mutex_t* reserveLogSpaceLock) {
    printf("CONSTRUCTING LOG RESPONSE...\n");

    // SAVE OFF PERTINENT INFO (FILE SIZE, LOG HEADER RESPONSE SIZE), BUILD HEADER STR
    if(message->is_val_msg) {

        message->responseHeadStrSize = strlen(LOGRESPONSEHEADERBASE)+lengthOfIntegerString(message->content_length, message)+strlen(message->filename)+strlen(message->method)+1;
        message->responseHeader = (char*)malloc(message->responseHeadStrSize * sizeof(char));
        snprintf(message->responseHeader, message->responseHeadStrSize, "%s /%s length %zd\n", message->method, message->filename, message->content_length);

        if (strncmp(message->method, "HEAD", strlen("HEAD")) != 0) { // VALID PUT OR GET WENT THROUGH, SIGNIFY TO ADD FILE BODY TO RESPONSE
            message->want_body_in_log = true;
            div_t contentLenDiv = div((int)message->content_length, 20);
            message->bodyResponseSize = message->content_length*3 + ((contentLenDiv.quot + ((contentLenDiv.rem > 0) ? 1:0)) * 9);
        }
    } else {
        message->responseHeadStrSize = strlen(LOGRESPONSEHEADERBASE)+strlen((char *)&message->headerStarts)+1;
        message->responseHeader = (char*)malloc(message->responseHeadStrSize * sizeof(char));
        snprintf(message->responseHeader, message->responseHeadStrSize, "FAIL: %s --- response %d\n", (char *)&message->headerStarts, message->status_code);
    }

    message->responseStrSize = strlen(message->responseHeader) + message->bodyResponseSize + strlen(LOGRESPONSECLOSE); // FIND SIZE OF RESPONSE TO BE LOGGED

    // CRIT REGION START LOCK
    pthread_mutex_lock(reserveLogSpaceLock);
    message->currLogOffset = log->logSizeOffset;
    log->logSizeOffset += message->responseStrSize;
    size_t spaceReserved = 0;
    memset(&message->buffer[0], 0, sizeof(message->buffer));
    message->buffer[BUFFER_SIZE] = '\0';
    while(message->currLogOffset+spaceReserved < message->responseStrSize) {
        if(spaceReserved <= (BUFFER_SIZE-1)) {
            snprintf((char *) &message->buffer+(spaceReserved%BUFFER_SIZE-1), 2, "1");
        }
        if ((message->responseStrSize - spaceReserved) < (BUFFER_SIZE-1)) {
            pwrite(log->logfd, message->buffer, (message->responseStrSize - spaceReserved), message->currLogOffset+spaceReserved);
            break;
        }
        if (spaceReserved%(BUFFER_SIZE-1)==0) {
            pwrite(log->logfd, message->buffer, BUFFER_SIZE-1, message->currLogOffset+spaceReserved);
        }
        spaceReserved++;
    }
    pthread_mutex_unlock(reserveLogSpaceLock);
    // CRIT REGION DONE, UNLOCK

    message->currLBytesWritten = pwrite(log->logfd, message->responseHeader, strlen(message->responseHeader), message->currLogOffset);
    message->currLogOffset += message->currLBytesWritten;

    free(message->responseHeader);

    return;
}

/*
    \brief 2. Want to process the message we just recieved
*/
void process_request(ssize_t client_sockd, struct httpObject* message, pthread_mutex_t* filenameCharCheckLock, struct logObject* log, pthread_mutex_t* reserveLogSpaceLock) {
    printf("Processing Request\n");

    // PROCESS FILENAME
    if(strlen(message->filename) > 27) {
        message->status_code = 400;
        message->is_val_msg = false;
        message->filename[strlen(message->filename)] = '\0';
    }

    if(message->is_val_msg) {
        pthread_mutex_lock(filenameCharCheckLock);
        for (size_t i = 0; i<strlen(message->filename); i++) {
            char candidate = message->filename[i];
            if(((candidate >= 65 && candidate <= 90) || (candidate >= 97 && candidate <= 122) || (candidate == 95) || (candidate == 45) || (candidate >= 48 && candidate <= 57)) && message->is_val_msg) {
                if(i==strlen(message->filename)-1) { // IF WE HAVE REACHED END OF FILENAME, NULL TERMINATE HOLDER AND CONTINUE
                    message->filename[strlen(message->filename)] = '\0';
                }
            } else {
                message->status_code = 400; // FILENAME HAS ILLEGAL CHARS OR IS > 27 IN LENGTH, SIGNAL BAD REQUEST
                message->is_val_msg = false;
                message->filename[strlen(message->filename)] = '\0';
                break;
            }
        }
        pthread_mutex_unlock(filenameCharCheckLock);
    }
    
    // PROCESS HTTPVERSION
    if(strncmp(message->httpversion, "HTTP/1.1", strlen("HTTP/1.1")) != 0) { // if invalid httpversion, set status code accordingly, otherwise continue
        message->status_code = 400; // HTTP VERSION IS BAD, SIGNAL BAD REQUEST
        message->is_val_msg = false;
        message->httpversion[strlen(message->httpversion)] = '\0';
    } else { // HTTPVERSION IS VALID, NULL TERMINATE HOLDER
        message->httpversion[strlen(message->httpversion)] = '\0';
    }

    //PROCESS METHOD TO CALL
    if(strncmp(message->method, PUTSTR, strlen(PUTSTR)) == 0 && strlen(message->method) == 3) { // RECEIVED PUT REQUEST
        strncpy(message->method, "PUT", strlen("PUT"));
        message->method[3] = '\0'; // GET RID OF EXTRA SPACE
        if(message->is_val_msg) {
            if(strncmp(message->filename, HEALTHCHECKSTR, strlen(HEALTHCHECKSTR))==0 && strlen(message->filename)==strlen(HEALTHCHECKSTR)) { // PUT HEALTHCHECK CASE
                message->status_code = 403;
                message->is_val_msg = false;
            } else {
                PUT(message);
            }
        }
    } else if (strncmp(message->method, GETSTR, strlen(GETSTR)) == 0 && strlen(message->method) == 3) { // RECEIVED GET REQUEST, SIGNAL TO SEND BODY AFTER RESPONSE HEADER
        strncpy(message->method, "GET", strlen("GET"));
        message->method[3] = '\0'; // GET RID OF EXTRA SPACE
        if(message->is_val_msg) {
            if(strncmp(message->filename, HEALTHCHECKSTR, strlen(HEALTHCHECKSTR))==0 && strlen(message->filename)==strlen(HEALTHCHECKSTR) && (message->log_is_live)) { 
                message->currTotalLogs = log->total_logs;
                message->currFailedLogs = log->failed_logs;
                message->status_code = 200;
                message->do_want_healthcheck = true;
            } else {
                GET_or_HEAD(message);
                message->do_send_File_Body = true;
            }
        }
    } else if (strncmp(message->method, HEADSTR, strlen(HEADSTR)) == 0 && strlen(message->method) == 4) { // RECEIVED HEAD REQUEST
        strncpy(message->method, "HEAD", strlen("HEAD"));
        message->method[4] = '\0'; // GET RID OF EXTRA SPACE
        if(message->is_val_msg) {
            if(strncmp(message->filename, HEALTHCHECKSTR, strlen(HEALTHCHECKSTR))==0 && strlen(message->filename)==strlen(HEALTHCHECKSTR)) { // IF HEAD HEALTHCHECK CASE
                message->status_code = 403;
                message->is_val_msg = false;
            } else {
                GET_or_HEAD(message);
            }
        }
    } else { // INVALID METHOD
        message->status_code = 400; //bad request, method could not be matched, DO NOT NEED THIS MOST LIKELY
        message->is_val_msg = false;
        message->method[strlen(message->method)] = '\0';
    }

    // SET CONTENT LENGTH IF HEALTHCHECK REQUESTED
    if(message->do_want_healthcheck) {
        message->content_length = lengthOfIntegerString(message->currFailedLogs, message)+1+lengthOfIntegerString(message->currTotalLogs, message);
    }

    // NOW RESERVE LOG SPACE
    if(log->want_response_log) {
        if(!(message->is_val_msg)) { // LOAD INVALID FIRST LINE UP TO \R\N IF WE LOG A FAIL
            memset(&message->headerStarts[0], 0, sizeof(message->headerStarts));
            sscanf((char*)&message->buffer, "%[^\r\n]s", (char*)&message->headerStarts);
            message->headerStarts[strlen((char*)&message->headerStarts)] = '\0';
        }
        log_response(message, log, reserveLogSpaceLock);
    }

    // VALID PUT CASE, WRITE CONTENTS
    if(message->is_val_msg && message->cl_wanted) { 
        memset(&message->buffer[0], 0, sizeof(message->buffer));

        if(message->is_body_in_header) { // IF BODY DATA STORED IN BUF, WRITE BUF TO FILE, THEN APPEND REMAINING BODY DATA ON SOCK TO FILE 
            memmove(message->buffer, message->headerStarts, message->bytesAfterHeaderCount);
            message->buffer[message->bytesAfterHeaderCount] = 0;
        } 

        copyFromSourceToDest(client_sockd, 0, message->filefd, message, log);
        close(message->filefd);
    }

    status_code_str(message->status_code, message->status_code_string); // SET STR ASSOCIATED WITH STATUS CODE
    return;
}

/*
    \brief 3. Construct some response based on the HTTP request you recieved
*/
void construct_http_response(struct httpObject* message) {

    if(message->is_val_msg && !(message->cl_wanted)) { // ON VALID REQUEST GET/HEAD CALCULATE STR LEN OF CONTENT LENGTH, SEND APPROPRIATE RESPONSE

        message->responseStrSize = strlen(RESPONSEBASE)+strlen(message->status_code_string)+lengthOfIntegerString(message->content_length, message)+1;
        message->responseHeader = (char*)malloc(message->responseStrSize * sizeof(char));
        snprintf(message->responseHeader, message->responseStrSize, "HTTP/1.1 %d %s\r\nContent-Length: %zd\r\n\r\n", message->status_code, message->status_code_string, message->content_length);
    } else { // ON INVALID REQUEST SEND STATUS CODE + STATUS STR ALONG WITH CONTENT LENGTH 0
        message->responseStrSize = strlen(RESPONSEBASE)+strlen(message->status_code_string)+1+1;
        message->responseHeader = (char*)malloc(message->responseStrSize * sizeof(char));
        snprintf(message->responseHeader, message->responseStrSize, "HTTP/1.1 %d %s\r\nContent-Length: %d\r\n\r\n", message->status_code, message->status_code_string, 0);
    }
    return;
}

/* CLEAN HTTP OBJECT FOR WORKER */

void httpObjectCleaner(struct httpObject* message) {
        memset(&message->buffer[0], 0, BUFFER_SIZE);
        memset(&message->filename[0], 0, sizeof(message->filename));
        memset(&message->httpversion[0], 0, sizeof(message->httpversion));
        memset(&message->method[0], 0, sizeof(message->method));
        memset(&message->convertedFileBody[0], 0, sizeof(message->convertedFileBody));
        memset(&message->status_code_string[0], 0, sizeof(message->status_code_string));
        memset(&message->headerStarts[0], 0, sizeof(message->headerStarts));
        memset(&message->headString1[0], 0, sizeof(message->headString1));
        memset(&message->statbufF, 0, sizeof(message->statbufF));
        memset(&message->socketIOcheck, 0, sizeof(message->socketIOcheck));
        message->responseHeader = NULL;
        message->content_length = 0;
        message->cl_wanted = false;
        message->cl_written = false;
        message->is_val_msg = true;
        message->do_send_File_Body = false;
        message->is_body_in_header = false;
        message->do_want_healthcheck = false;
        message->log_is_live = false;
        message->want_body_in_log = false;
        message->firstHeader = true;
        message->status_code = 500;
        message->writeToDestinationOffset = 0;
        message->currLogOffset = 0;
        message->currDBytesWritten = 0;
        message->currLBytesWritten = 0;
        message->bytes_converted_from_buffer = 0;
        message->bytesToConvertInLine = 0;
        message->bytefoldover = 0;
        message->total_file_bytes_seen = 0;
        message->total_bytes_written_to_log = 0;
        message->bytesConvertedInLine = 0;
        message->bytesReadInLine = 0;
        message->filefd = -1;
        message->bodyResponseSize = 0;
        message->responseStrSize = 0;
        message->responseHeadStrSize = 0;
        message->numberScanned = 0;
        message->bytesAfterHeaderCount = 0;
        message->numOfReceivedBytes = 0;
        message->read_bytes = 0;
        message->pollReturn = 0;
        message->bytesLeftToWrite = 0;
        message->numberStrSize = 1;
        message->numCopy = 0;
        message->currFailedLogs = 0;
        message->currTotalLogs = 0;

        
    return;
}

/* worker thread structure */
struct worker {

    int id;
    pthread_t worker_id;
    struct httpObject message;
    struct logObject* log;
    int client_sockd;
    pthread_cond_t condition_var;
    pthread_mutex_t* lock;
    pthread_mutex_t* stringFinderLock;
    pthread_mutex_t* reserveLogSpaceLock;
    pthread_mutex_t* filenameCharCheckLock;
    pthread_mutex_t* incrementLogTotalsLock;
    bool workerThreadAvailable;

};

void* handle_request(void* thread) {
    struct worker* w_thread = (struct worker*)thread;
    printf("[+] server is waiting...\n");
    //the worker in a way is a consumer
    
    while(true) {
        printf("THREAD SPINNING ID: %d\n", w_thread->id);
        // while we don't have a valid client socket, we wait
        while(w_thread->client_sockd < 0) {
            int rc = pthread_cond_wait(&w_thread->condition_var, w_thread->lock);
            //printf("return of wait: %d\n", rc);
        }

        httpObjectCleaner(&w_thread->message); // memSet all pieces of httpObject to start values.
        w_thread->message.log_is_live = w_thread->log->want_response_log;

        // PROCESS READ HTTP REQUEST
        read_http_response(w_thread->client_sockd, &w_thread->message, w_thread->stringFinderLock);

        // PROCESS AND SET UP LOG IF WANTED
        process_request(w_thread->client_sockd, &w_thread->message, w_thread->filenameCharCheckLock, w_thread->log, w_thread->reserveLogSpaceLock);

        // CONSTRUCT RESPONSE AND SEND HEADER RESPONSE
        construct_http_response(&w_thread->message);
        send(w_thread->client_sockd, w_thread->message.responseHeader, strlen(w_thread->message.responseHeader), 0); // SEND CONSTRUCTED REPSPONSE HEAD TO CLIENT
        free(w_thread->message.responseHeader);
        
        // VALID GET CASE, SEND CONTENTS
        if(w_thread->message.is_val_msg && w_thread->message.do_send_File_Body && !(w_thread->message.do_want_healthcheck)) { // IF GET REQUESTED, SEND CONTENTS OF FILE REQUESTED
            memset(&w_thread->message.buffer[0], 0, sizeof(w_thread->message.buffer));
            w_thread->message.socketIOcheck.events = POLLOUT;
            copyFromSourceToDest(w_thread->message.filefd, -1, w_thread->client_sockd, &w_thread->message, w_thread->log);
            close(w_thread->message.filefd);
        }

        // GET HEALTHCHECK CASE, SEND AND LOG CONTENTS
        if(w_thread->message.is_val_msg && w_thread->message.do_want_healthcheck) {
            //printf("we sending health check to client\n");
            w_thread->message.responseHeader = (char*)malloc((w_thread->message.content_length+1) * sizeof(char));
            snprintf(w_thread->message.responseHeader, (w_thread->message.content_length+1), "%d\n%d", w_thread->message.currFailedLogs, w_thread->message.currTotalLogs);
            send(w_thread->client_sockd, w_thread->message.responseHeader, strlen(w_thread->message.responseHeader), 0);

            memcpy(w_thread->message.buffer, w_thread->message.responseHeader, strlen(w_thread->message.responseHeader));
            w_thread->message.buffer[strlen(w_thread->message.responseHeader)] = '\0';

            writeHexBodyToLog(&w_thread->message, w_thread->log, w_thread->message.content_length);
            free(w_thread->message.responseHeader);

        }

        if(w_thread->log->want_response_log) { // IF WE LOGGED A RESPONSE CLOSE OFF RESPONSE AND INCREMENT LOG COUNTERS
            pwrite(w_thread->log->logfd, LOGRESPONSECLOSE, strlen(LOGRESPONSECLOSE), w_thread->message.currLogOffset);
            pthread_mutex_lock(w_thread->incrementLogTotalsLock);
            if(!(w_thread->message.is_val_msg)) {
                w_thread->log->failed_logs+=1; // INCREMENT ERROR LOGS
            }
            w_thread->log->total_logs+=1; // INCREMENT AMOUNT OF LOGS SEEN
            pthread_mutex_unlock(w_thread->incrementLogTotalsLock);
        }

        close(w_thread->client_sockd);
        w_thread->client_sockd = INT_MIN; //to sleep again
        
        //printf("this many seconds so far: %f\n", ((double)clock()/CLOCKS_PER_SEC));
    }
}

int8_t checkValidLogFile(struct logObject* log) { // CHECK TO MAKE SURE LOGFILE CAN BE OPENED OVER EXISTING FILE OR CREATE NEW ONE
    struct stat statbufLF;
    //int fd;
    stat(log->logfilename, &statbufLF);

    if(access(log->logfilename, F_OK) > -1) { // ENTITY EXISTS WITH NAME
        if (!(statbufLF.st_mode & S_IWUSR)) { // FORBIDDEN, ENTITY EXISTS WITH SAME NAME BUT IS NOT A FILE/FILE CANNOT BE WRITTEN TO
            return -1;
        }
    }

    log->logfd = open(log->logfilename, O_CREAT | O_RDWR | O_TRUNC, 0644);
    if (log->logfd == -1) { // FILE COULD NOT BE OPENED/CREATED WITH THESE PERMISSIONS
        return -1;
    }

    return 0;
}

int main(int argc, char** argv) {

    int amountOfThreads = 4;
    char* port = NULL;
    char* log_filename = NULL;
    int c;

    opterr = 0;

    while ((c = getopt(argc, argv, ":N:l:")) != -1) {
        switch (c) {
            case 'N':
                if (strncmp(optarg, "-l", strlen("-l")) == 0) {
                    fprintf(stderr, "-N needs a valid argument\n");
                    return EXIT_FAILURE;
                }
                amountOfThreads = atoi(optarg);
                break;
            case 'l':
                if(strlen(optarg)>255) { // CHECKING IF LOGFILENAME IS LONGER THAN ALLOWED (255 bytes max linux filename size)
                    fprintf(stderr, "-l needs a valid filename (less than 255 byte linux limit)\n");
                    return EXIT_FAILURE;
                } else if (strncmp(optarg, "-N", strlen("-N")) == 0) {
                    fprintf(stderr, "-l needs a valid argument\n");
                    return EXIT_FAILURE;
                } else {
                    log_filename = optarg;
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

    port = argv[optind];

    struct logObject log;
    log.want_response_log = false;

    if(log_filename != NULL) {
        log.want_response_log = true;
        strncpy(log.logfilename, log_filename, strlen(log_filename)+1);
        log.logfilename[strlen(log_filename)] = '\0';
        if((checkValidLogFile(&log)) == -1) {return EXIT_FAILURE;}
        log.logSizeOffset = 0;
        log.total_logs = 0;
        log.failed_logs = 0;
    }

    /*
        Create sockaddr_in with server information
    */

    struct sockaddr_in server_addr;
    memset(&server_addr, 0, sizeof(server_addr));
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(atoi(port));
    server_addr.sin_addr.s_addr = htonl(INADDR_ANY);
    socklen_t addrlen = sizeof(server_addr);

    /*
        Create server socket
    */
    int server_sockd = socket(AF_INET, SOCK_STREAM, 0);

    // Need to check if server_sockd < 0, meaning an error
    if (server_sockd < 0) {
        perror("socket");
    }

    /*
        Configure server socket
    */
    int enable = 1;

    /*
        This allows you to avoid: 'Bind: Address Already in Use' error
    */
    int ret = setsockopt(server_sockd, SOL_SOCKET, SO_REUSEADDR, &enable, sizeof(enable));

    /*
        Bind server address to socket that is open
    */
    ret = bind(server_sockd, (struct sockaddr *) &server_addr, addrlen);

    /*
        Listen for incoming connections
    */
    ret = listen(server_sockd, 5); // 5 should be enough, if not use SOMAXCONN

    if (ret < 0) {
        return EXIT_FAILURE;
    }

    /*
        Connecting with a client
    */
    struct sockaddr client_addr;
    socklen_t client_addrlen = sizeof(client_addr);

    pthread_mutex_t lock = PTHREAD_MUTEX_INITIALIZER; // lock to put on threads when not in use
    pthread_mutex_t filenameCharCheckLock = PTHREAD_MUTEX_INITIALIZER;
    pthread_mutex_t stringFinderLock = PTHREAD_MUTEX_INITIALIZER;
    pthread_mutex_t reserveLogSpaceLock = PTHREAD_MUTEX_INITIALIZER;
    pthread_mutex_t incrementLogTotalsLock = PTHREAD_MUTEX_INITIALIZER;
    pthread_cond_t condt = PTHREAD_COND_INITIALIZER;
    bool workerThreadAvailable = false;
    struct worker workers[amountOfThreads];
    int is_error = 0;

    for (int i = 0; i < amountOfThreads; i++) {
        workers[i].client_sockd = INT_MIN;
        workers[i].id = i;
        workers[i].condition_var = condt;
        workers[i].lock = &lock;
        workers[i].log = &log;
        workers[i].workerThreadAvailable = workerThreadAvailable;
        workers[i].stringFinderLock = &stringFinderLock;
        workers[i].reserveLogSpaceLock = &reserveLogSpaceLock;
        workers[i].filenameCharCheckLock = &filenameCharCheckLock;
        workers[i].incrementLogTotalsLock = &incrementLogTotalsLock;
       
        is_error = pthread_create(&workers[i].worker_id, NULL, handle_request, (void *)&workers[i]);
        
        if (is_error) {
            return EXIT_FAILURE;
        }
    }

    //bool workerThreadFound = false;
    int target_thread = 0;
    int count = 0;
    timeForProgram = 0;
    while (true) {

        /*
         * 1. Accept Connection
         */
        int client_sockd = accept(server_sockd, &client_addr, &client_addrlen);

        while(1) { // LOOK FOR READY THREAD, BROADCAST IF FOUND, ELSE USLEEP .01S AND LOOK AGAIN
            target_thread = count%amountOfThreads;
            if(workers[target_thread].client_sockd < 0) {
                workers[target_thread].client_sockd = client_sockd;
                pthread_cond_broadcast(&workers[target_thread].condition_var);
                break;
            }
            usleep(1000);
            count++;
        }
    }

    close(log.logfd);

    for (int i = 0; i < amountOfThreads; i++) {
        memset(&workers[i], 0, sizeof(workers[i]));
    }

    return EXIT_SUCCESS;
}
