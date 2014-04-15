#the beginning of a client instance
import socket
import sys
import os
import time
import Global
import threading
import Global_client


def file_transfer(s, data):  # reply: filetransfer <sender> <receiver> <filename>
    predir = os.getcwd()
    try:
        file = open(predir+'/' + data[3], 'rb')
    except:
        print "File not exists. Please try again."
        s.send("filetransferdec " + data[1] + " " + data[2] + " " + data[3])
        return
    s.send("filetransfer " + data[1] + " " + data[2] + " " + data[3])
    print "Now begin transfering, please wait..."
    #--------
    data = s.recv(4096)
    if data == 'ready':
        while True:
            data = file.read(4096)
            if not data:
                break
            s.sendall(data)
        file.close()
        time.sleep(1)
        s.sendall('EOF')
        print "Transferring process succeeds."
    else:
        print "some errors happen during the transfer process. continue t=other operations."
    #--------
    return


def file_receiver(s, data):
    print "server ready, now client receive file"
    print "Please wait until the \"receive file success\" notification has raised!..."
    predir = os.getcwd()
    f = open(predir+'/' + "rev_" + data[2], 'wb')
    s.sendall("ready")
    while True:
        data = s.recv(4096)
        if data == 'EOF':
            print "receive file success!"
            break
        f.write(data)
    f.close()
    return

def receiver(s, username):
    # the seperate thread designed for receiving message (no matter what kind of - private, broadcast) from the host
    while 1:
        try:
            reply = s.recv(4096)
        except:
            print "Some errors happened. But no problem. I will continue."
            print "Can't receive message from the server. Maybe the server has stopped via closing the terminal window directly. This client program will terminate right now!."
            Global_client.event.set()
            return
        reply = reply.strip()

        if reply[0:7] == "maxuser":  # if the user # has reached the upper limitation, we should logout directly
            print reply[9:]
            Global_client.event.set()
            return
        if reply == "logout":  # "logout" is the logout AKW
            print "You have logged out! See you again!"
            Global_client.event.set()
            return
        if reply == "quit":  # "logout" is the logout AKW
            print "You are leaving the chatting room! See you again!"
            Global_client.event.set()
            return
        if reply == "termination":  # "logout" is the logout AKW; this situation actually is due to the main thread quit, so we don't do anything to inform that thread
            Global_client.event.set()
            return
        # here are some situations that we can't log out the main waiting thread
        if reply == "terminate":  # because of block related things happen
            print "Wrong password for 3 times! Connection terminated! And you are blocked!"
            Global_client.event.set()
            return
        if reply[:7] == "timeout":  # because of timeout issue happen
            s.send("timeout")
            print "Time out for " + reply[7:] + " seconds."
            Global_client.event.set()
            return
        if reply == "serverstop":  # because of block related things happen
            s.send("serverstop")
            print "The server is going to stop due to some reasons (system error or administrator operation). You will log out from the server automatically."
            Global_client.event.set()
            return
        if reply[:12] == "filetransfer":
            reply = reply.split(" ")
            file_transfer(s, reply)
            continue
        if reply[:10] == "file_ready":
            reply = reply.split(" ")
            file_receiver(s, reply)
            continue
        print reply
    return

def sender(s, username):
    while 1:
        try:
            input = raw_input()
        except KeyboardInterrupt:  # capture the "Ctrl+C" quit out; actually we can't capture this exception because it is in another env
            s.send("termination")
            print "The Client program has been brutely terminated!..."
            break
        input = input.strip()
        if input == "":  # empty entering handled here, which means that the client is unactive
            print "Please enter an instruction as above. No empty operation is permitted."
            print username + ">>"
            continue
        try:
            s.send(input)
        except socket.error:  # this kind of
            break


if __name__ == '__main__':
    # start from the very beginning, accept the IP address and Port Number from the user input in the console
    if len(sys.argv) != 3:
        print "Please follow this format to run the Client program:"
        print "python Client.py 10.10.10.12 1234"
        print "(python stript_name IP Port)"
        sys.exit()
    HOST = sys.argv[1]
    PORT = int(sys.argv[2])

    #HOST = Global.HOST
    #PORT = Global.PORT

    #----------------- create a new socket -----------------
    try:
        s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    except socket.error, msg:
        print 'Failed to create socket. Error code: ' + str(msg[0]) + ' , Error message: ' + msg[1]
        sys.exit()

    #----------------- connect the remote host with this socket, and the designated Port Number -----------------
    try:
        s.connect((HOST, PORT))
    except socket.error, msg:
        print 'Failed to connect the host. Error code: ' + str(msg[0]) + ' , Error message: ' + msg[1]
        sys.exit()

    #before the normal operation, we should receive the welcome information first -- this is the blocking status for the connection
    reply = s.recv(4096)
    reply = reply.strip()

    # for the maximum user problem, we don't even enter the main thread and the receiver thread
    if reply[0:7] == "maxuser":  # if the user # has reached the upper limitation, we should logout directly
        print reply[9:]
        s.close()
        sys.exit()

    print reply  # always be the "welcome..."
    print ">>"

    #---------------- the log in module -------------------
    while 1:
        try:
            input = raw_input()
        except KeyboardInterrupt:  # capture the "Ctrl+C" quit out; actually we can't capture this exception because it is in another env
            s.send("termination")  #  there are two kinds of "termination", before logging-in and after logging-in, all come from KeyboardInterupt
            print "The Client program has been abruptly terminated even before the user has logged in!..."
            s.close()
            sys.exit()
        input = input.strip()
        if input == "":  # empty entering handled here, which means that the client is unactive
            print "Please enter an effective user-name or instruction as above. No empty operation is permitted."
            print ">>"
            continue
        try:
            s.sendall(input)
        except socket.error:  # TODO note here, only by two times used this kind of error can be detected, but this is not normal because server down is not normal
            print "There are some socket errors in this connection session. Maybe the server has stopped. The client program will terminate right now."
            s.close()
            sys.exit()
        if input == "quit":
            print "You have quited the Client program. See you again!"
            s.close()
            sys.exit()
        try:
            reply = s.recv(4096)
        except:
            print "There are some socket errors in this connection session. Maybe the server has stopped via closing the terminal windows directly. The client program will terminate right now."
            s.close()
            sys.exit()
        if reply[:10] == "logsuccess":  # successfully logged in
            reply = reply.split("@@@")
            print reply[0][10:]
            username = reply[1]
            break
        print reply

    #--------------------- starting the receiver thread --------------------------
    new_thread = threading.Thread(target=receiver, args=(s, username))
    new_thread.setDaemon(True)
    new_thread.start()
    #--------------------- starting the receiver thread --------------------------
    new_thread = threading.Thread(target=sender, args=(s, username))
    new_thread.setDaemon(True)  # if we terminate this main waiting-to-logout thread, this sender sub-thread will be terminated
    new_thread.start()

    #------------------------------ the user command thread (main thread) ----------------------------------
    try:
        Global_client.event.wait()  # we wait the signal from the receiver because by doing this we can avoid closing socket during we are still listening
        s.close()
        Global_client.event.clear()
        # after this thread quit, the sender thread will quit as well
    except KeyboardInterrupt:  # capture the "Ctrl+C" quit out TODO can we?
        pass
        #s.send("termination")
        #Global_client.event.wait()
        #s.close()
        #Global_client.event.clear()
        #print "The Client program has been brutely terminated!..."
        # after this thread quit, the sender thread will quit as well