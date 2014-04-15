#the main server script, listening to client connection
import socket
import sys
import os
import threading
from thread import *
from Server_client import *
import Global
ISOTIMEFORMAT='%Y-%m-%d_%X'


def server_stop_notif():  # just like a broadcast thread, to notify every connected clients to leave
    for user in Global.list_user:
        message = Global.message("System", user.name, "serverstop")
        Global.message_rep[user.name].append(message)
        Global.event[user.name].set()
    disp = "The server_stop notification has been sent to all the online clients, and they will automatically log out right now."
    print disp
    Global.log.write(disp + "\n")
    #------------ we should do the database backup task right here ------------
    Global.save_para(Global.MaxCon, Global.BLOCK_TIME, Global.LAST_HOUR, Global.TIME_OUT)
    disp = "[backup]MaxCon, BLOCK_TIME, LAST_HOUR, TIME_OUT all have been stored."
    print disp
    Global.log.write(disp + "\n")

    Global.save_u_p()
    disp = "[backup]user_password repository has been stored."
    print disp
    Global.log.write(disp + "\n")

    Global.save_message_rep()
    disp = "[backup]message_rep has been stored."
    print disp
    Global.log.write(disp + "\n")

    Global.save_file_rep()
    disp = "[backup]file_rep has been stored."
    print disp
    Global.log.write(disp + "\n")

    Global.save_block_rep()
    disp = "[backup]block_rep has been stored."
    print disp
    Global.log.write(disp + "\n")

    Global.save_list_block()
    disp = "[backup]list_block has been stored."
    print disp
    Global.log.write(disp + "\n")
    #---------------------------- backup done ---------------------------------
    return

def ServerListen(s):
    while 1:
        # wait to accept a connection - blocking call
        try:  # actually this KeyboardInterrupt can not be captured, because we don't interact in this environment in the console
            connect, ad = s.accept()  # this blocking status should be deal with so I bring another level of thread
        except:  # this is for the server stop presently

            #DEBUG
            disp = "listern..."
            print disp
            Global.log.write(disp + "\n")

            new_thread = threading.Thread(target=server_stop_notif)
            new_thread.setDaemon(True)
            new_thread.start()
            new_thread.join()
            disp = "The server is being stopped via some server problems."  # actually this will not always happen
            print disp
            #Global.log.write(disp + "\n")
            #please perform all the necessary operations
            break
        # these codes should be omitted, because the exception may not be captured otherwise
        # TODO I should protect the global data
        disp = 'Connected with ' + ad[0] + ':' + str(ad[1])
        print disp
        Global.log.write(disp + "\n")
        start_new_thread(client, (connect, ad))

    #time.sleep(2)  # waiting for all the server_receiver threads to be terminated, otherwise the blocked connect.recv(1024)
                    # function will be affected by the following s.close() (at least it is possible)
                    # BUT, actually this is not necessary, because the above connect.recv(1024) has exception detection
    while len(Global.list_user) != 0:
        pass
    s.close()
    Global.SERVER_STOP = True
    return


def ServerOperation():  # this is a administration thread
    while 1:
        input = raw_input()
        input = input.strip()
        if input == "stop":
            new_thread = threading.Thread(target=server_stop_notif)
            new_thread.setDaemon(True)
            new_thread.start()
            new_thread.join()
            disp = "The server is being stopped via administrator operation."
            print disp
            Global.log.write(disp + "\n")
            #time.sleep(2)  # waiting for all the server_receiver threads to be terminated, otherwise the blocked connect.recv(1024)
                    # function will be affected by the following s.close() (at least it is possible)
                    # BUT, actually this is not necessary, because the above connect.recv(1024) has exception detection
            while len(Global.list_user) != 0:  # this means that we should change the list_user after we actually stop that client-server connection
                pass
            s.close()
            Global.SERVER_STOP = True
            return

        elif input == "online users":
            disp = "[admin]The present online users are:"
            print disp
            Global.log.write(disp + "\n")
            for user in Global.list_user:
                disp = user.name + " on " + user.ip + ':' + str(user.port)
                print disp
                Global.log.write(disp + "\n")

        elif input == "blocked users":
            disp = "[admin]The present blocked users are:"
            print disp
            Global.log.write(disp + "\n")
            N = 0
            for user in Global.list_block:
                if not user.get_bool():
                    continue
                t = time.strftime(ISOTIMEFORMAT, time.localtime(user.start))
                disp = user.name + " on " + user.ip + ' at ' + t
                print disp
                Global.log.write(disp + "\n")
                N += 1
            if N == 0:
                print "There are no blocked users by now."

        elif input == "all users":
            disp = "[admin]The present all users are:"
            print disp
            Global.log.write(disp + "\n")
            for user in Global.u_p:
                disp = "\"" + user + "\" with password \"" + Global.u_p[user] + "\""
                print disp
                Global.log.write(disp + "\n")

        elif input == "MaxCon":  # in seconds in system
            disp = "[admin]The present permittable maximum user connection # is:"
            print disp
            Global.log.write(disp + "\n")
            disp = str(Global.MaxCon)
            print disp
            Global.log.write(disp + "\n")

        elif input == "BLOCK_TIME":  # in seconds in system
            disp = "[admin]The present BLOCK_TIME is:"
            print disp
            Global.log.write(disp + "\n")
            disp = str(Global.BLOCK_TIME) + " seconds"
            print disp
            Global.log.write(disp + "\n")

        elif input == "LAST_HOUR":  # in seconds in system
            disp = "[admin]The present LAST_HOUR is:"
            print disp
            Global.log.write(disp + "\n")
            #disp = str(Global.LAST_HOUR/3600) + " hours"
            disp = str(Global.LAST_HOUR) + " seconds"
            print disp
            Global.log.write(disp + "\n")

        elif input == "TIME_OUT":  # in seconds in system
            disp = "[admin]The present TIME_OUT is:"
            print disp
            Global.log.write(disp + "\n")
            #disp = str(Global.TIME_OUT/60) + " minutes"
            disp = str(Global.TIME_OUT) + " seconds"
            print disp
            Global.log.write(disp + "\n")

        elif input == "change MaxCon":
            disp = "[admin]Please enter your new MaxCon parameter: (in int format)"
            print disp
            Global.log.write(disp + "\n")
            input = raw_input()
            input = input.strip()
            try:
                Global.MaxCon = int(input)
            except:
                print "No change. You entered something we can't recognize. Sorry."
                continue
            disp = "The MaxCon has been changed to " + str(Global.MaxCon)
            print disp
            Global.log.write(disp + "\n")

        elif input == "change BLOCK_TIME":
            disp = "[admin]Please enter your new BLOCK_TIME parameter: (in float format and it will represent how many seconds)"
            print disp
            Global.log.write(disp + "\n")
            input = raw_input()
            input = input.strip()
            try:
                Global.BLOCK_TIME = float(input)
            except:
                print "No change. You entered something we can't recognize. Sorry."
                continue
            disp = "The BLOCK_TIME has been changed to " + str(Global.BLOCK_TIME)
            print disp
            Global.log.write(disp + "\n")

        elif input == "change LAST_HOUR":
            #disp = "[admin]Please enter your new LAST_HOUR parameter: (in float format and it will represent how many hours)"
            disp = "[admin]Please enter your new LAST_HOUR parameter: (in float format and it will represent how many seconds)"
            print disp
            Global.log.write(disp + "\n")
            input = raw_input()
            input = input.strip()
            #Global.LAST_HOUR = float(input) * 3600
            #disp = "The LAST_HOUR has been changed to " + str(Global.LAST_HOUR/3600)
            try:
                Global.LAST_HOUR = float(input)
            except:
                print "No change. You entered something we can't recognize. Sorry."
                continue
            disp = "The LAST_HOUR has been changed to " + str(Global.LAST_HOUR)
            print disp
            Global.log.write(disp + "\n")

        elif input == "change TIME_OUT":
            #disp = "[admin]Please enter your new TIME_OUT parameter: (in float format and it will represent how many minutes)"
            disp = "[admin]Please enter your new TIME_OUT parameter: (in float format and it will represent how many seconds)"
            print disp
            Global.log.write(disp + "\n")
            input = raw_input()
            input = input.strip()
            #Global.TIME_OUT = float(input) * 60
            #disp = "The TIME_OUT has been changed to " + str(Global.TIME_OUT/60)
            try:
                Global.TIME_OUT = float(input)
            except:
                print "No change. You entered something we can't recognize. Sorry."
                continue
            disp = "The TIME_OUT has been changed to " + str(Global.TIME_OUT)
            print disp
            Global.log.write(disp + "\n")
        else:
            print "Command from the administrator can't be recognized! Please continue."


if __name__ == '__main__':
    # start from the very beginning, accept the Port Number from the user input in the console
    if len(sys.argv) != 2:
        print "Please follow this format to run the Server program:"
        print "python Server.py 1234"
        print "(python stript_name Port)"
        sys.exit()
    HOST = socket.gethostbyname(socket.gethostname())
    PORT = int(sys.argv[1])

    #HOST = Global.HOST
    #PORT = Global.PORT # Arbitrary non-privileged port

    #----------------- create a new socket -----------------
    try:
        s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    except socket.error, msg:
        print 'Failed to create socket. Error code: ' + str(msg[0]) + ' , Error message: ' + msg[1]
        sys.exit()

    #----------------- bind the socket with the IP and Port number -----------------
    try:
        s.bind((HOST, PORT))
    except socket.error, msg:
        print 'Socket bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
        sys.exit()
    print "Server is running now..."

    #-------------------- create the log file for the server ----------------------
    t = time.strftime(ISOTIMEFORMAT, time.localtime(time.time()))
    Global.log = open(os.getcwd() + "/" + "log_" + t + ".log", 'w')
    Global.log.write("Server is running now. Here is the log for this server, starting from " + t + ":\n")


    # always listening for the connection request from the users
    s.listen(10)
    disp = 'Server is listening for connections now...'
    print disp
    Global.log.write(disp + "\n")

    #----------------------- open the server_admin thread ----------------------
    new_thread = threading.Thread(target=ServerOperation)
    new_thread.setDaemon(True)
    new_thread.start()

    #----------------------- open the server_input_listen thread ----------------------
    new_thread = threading.Thread(target=ServerListen, args=(s,))
    new_thread.setDaemon(True)
    new_thread.start()
    while 1:  # check whether we should log out at regular time interval
        try:  # the server_stop KeyboardInterrupt will affect here
            # for fear that the SERVER_STOP mark is changed before all the client-server thread is killed, we should both check
            # the SERVER_STOP mark and whether there are still users in the online-list
            if Global.SERVER_STOP:
                disp = "The server has stoped! Bye!"
                print disp
                Global.log.write(disp + "\n")
                #------------------- save the server log ---------------------------
                disp = "[backup]server log has been saved."
                print disp
                Global.log.write(disp + "\n")

                t = time.strftime(ISOTIMEFORMAT, time.localtime(time.time()))
                Global.log.write("The server stopped at " + t + "\n")
                Global.log.close()
                #-------------------------------------------------------------------
                break
            time.sleep(Global.SERVER_CHECK)
        except:  # TODO I don't know why this quit method still can't free the port sometimes
                # TODO maybe some outside issues exist
            # I can capture the KeyboardInterupt here!!
            new_thread = threading.Thread(target=server_stop_notif)
            new_thread.setDaemon(True)
            new_thread.start()
            new_thread.join()
            disp = "The server is being stopped via \"Ctrl+C\"."
            print disp
            Global.log.write(disp + "\n")
            #please perform all the necessary operations
            while len(Global.list_user) != 0:
                pass
            #------------------- save the server log ---------------------------
            disp = "[backup]server log has been saved."
            print disp
            Global.log.write(disp + "\n")

            t = time.strftime(ISOTIMEFORMAT, time.localtime(time.time()))
            Global.log.write("The server stopped at " + t + "\n")
            Global.log.close()
            #-------------------------------------------------------------------
            s.close()
            break