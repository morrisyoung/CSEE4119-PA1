#interaction with the instanced client program, including login, blocked information, commands etc.
import Global
import time
import threading
import Server_command


def server_sender(connect, ad, name):
    # CAUTION: I want to use the setDaemon to terminate this sub-thread, because there are no important tasks going on.
    # I don't need to care about the resources re-storing problem, because this thread is only responsible for
    # simple sending task -----> wrong wrong wrong !!! I must close this thread, because I should close the socket used by this thread!!!
    # SO, now this thread can terminate appropriately!!
    #-------------- deal with the off-line messages for this user during its off-line time ---------------
    message=Global.message_rep[name]
    N=len(message)
    if N != 0:
        connect.sendall("The off-line messages during you are not in:\n")
    for i in range(N):
        t=message[i]
        reply= t.sender + ": " + t.content + "\n"
        connect.sendall(reply)
    del Global.message_rep[name][0:N]
    if N != 0:
        connect.sendall("Now you can input commands as above instructed:\n" + name + ">>\n")

    #-------------- deal with the normal private message ----------------
    while 1:
        Global.event[name].wait()
        Global.lock[name].acquire()
        while len(Global.message_rep[name]) != 0:  # just pop all the messages for that user
            message = (Global.message_rep[name]).pop()
            #---------------- added the server stop operation -----------------
            if message.sender == "System" and message.content == "serverstop":
                connect.sendall("serverstop")
                Global.lock[name].release()
                return
            if message.sender == "System" and message.content == "logout":  # if the user want to logout, we should terminate this thread!!
                Global.lock[name].release()
                return
            reply = message.sender + ": " + message.content + "\n" + name + ">>"
            #print reply + "haha"
            #print connect
            connect.sendall(reply)
            #print "I've sent the notif."
            # temporarily don't check the left messages from others, meaning that each time I just pop one thing from the list
        Global.lock[name].release()
        Global.event[name].clear()
    return


def server_receiver(connect, ad, name, user):
    #----------------------- the main command part -----------------------
    while True:
        #======================================
        (data, quit) = check_input(connect, ad)
        Global.list_lastop[name] = time.time()  # very important here!!!
        if quit:
            if data != "serverstop":
                # add a new feature: new user logging out notification
                levuser_notif(name)  # only when the user has actually logged in, this operation can be used when he log out
            #------------- let his personal sending thread to terminate ----------------
                message = Global.message("System", name, "logout")
                Global.message_rep[name].append(message)
                Global.event[name].set()
            break
        #======================================

        data = data.split(" ")  # even one word can form a ["xxx"] format
        reply = "You have chosen the following commands: " + data[0] + "\n"
        if data[0] not in Global.command:
                response = "But the command is not supported, please enter a supported command!\n"
                reply = reply + response + name + ">>"
                try:
                    connect.sendall(reply)
                except:
                    disp1 = "Some errors happened in the client side, because the host can't receive the data normally!" + "\n"
                    disp2 = "Maybe the user directly close the running terminal windows!\n"
                    disp3 = "This server-client interaction thread will terminate right now!" + "\n"
                    disp4 = 'Disconnected with ' + ad[0] + ':' + str(ad[1]) + ' because some errors happened in the client side.'
                    disp = disp1 + disp2 + disp3 + disp4
                    print disp
                    print "here we go!!!"
                    Global.log.write(disp + "\n")
                    levuser_notif(name)  # only when the user has actually logged in, this operation can be used when he log out
                    #------------- let his personal sending thread to terminate ----------------
                    message = Global.message("System", name, "logout")
                    Global.message_rep[name].append(message)
                    Global.event[name].set()
                    break
                disp = "User \"" + name + "\" has performed a command of \"" + data[0] + "\" on " + ad[0] + ':' + str(ad[1]) + " but this is not supported."
                print disp
                Global.log.write(disp + "\n")
        else:
            # supported command, operation should be performed
            Server_command.command_res(connect, data, name, ad)
    #---------------------- client-server interaction done, leaving now ------------------------
    disp = 'Server finished communication with ' + name + '. Disconnected with ' + ad[0] + ':' + str(ad[1])
    print disp
    Global.log.write(disp + "\n")

    # TODO when the server is stopping, there will be a huge data concurrency (actually not that huge). we should think about it
    connect.close()

    Global.list_user.remove(user)
    Global.lock_con.acquire()
    Global.con -= 1
    Global.lock_con.release()
    Global.lasthr_rep[name]=time.time()  # default value is None
    #DEBUG
    print "The present active users list:"
    print Global.list_user
    return


def check_input_early(connect, ad):
    # check for "logout" and "quit" and "termination" situations; only before the user has been logged in
    try:
        data = connect.recv(1024)
    except:
        disp1 = "Some errors happened in the client side, because the host can't receive the data normally!" + "\n"
        disp2 = "Maybe the user directly close the running terminal windows!\n"
        disp3 = "This server-client interaction thread will terminate right now!" + "\n"
        disp4 = 'Disconnected with ' + ad[0] + ':' + str(ad[1]) + ' because some errors happened in the client side.'
        disp = disp1 + disp2 + disp3 + disp4
        print disp
        Global.log.write(disp + "\n")
        return (None, True)
    data = data.strip()
    if data == "quit":
        connect.sendall("quit")
        disp = 'Disconnected with ' + ad[0] + ':' + str(ad[1]) + ' because the logger wants to leave directly.'
        print disp
        Global.log.write(disp + "\n")
        return (data, True)
    if data == "termination":
        disp = 'Disconnected with ' + ad[0] + ':' + str(ad[1]) + ' because the logger abruptly leave using \"Ctrl+C\".'
        print disp
        Global.log.write(disp + "\n")
        return (data, True)
    return (data, False)


def check_input(connect, ad):
    # check for "logout" and "quit" and "termination" situations
    try:
        data = connect.recv(1024)
    except:
        disp1 = "Some errors happened in the client side, because the host can't receive the data normally!" + "\n"
        disp2 = "Maybe the user directly close the running terminal windows!\n"
        disp3 = "This server-client interaction thread will terminate right now!" + "\n"
        disp4 = 'Disconnected with ' + ad[0] + ':' + str(ad[1]) + ' because some errors happened in the client side.'
        disp = disp1 + disp2 + disp3 + disp4
        print disp
        Global.log.write(disp + "\n")
        return (None, True)
    data = data.strip()
    if data == "termination":
        connect.sendall("termination")
        disp = 'Disconnected with ' + ad[0] + ':' + str(ad[1]) + ' because the logger brutely leave using \"Ctrl+C\".'
        print disp
        Global.log.write(disp + "\n")
        return (data, True)
    if data == "quit":
        connect.sendall("quit")
        disp = 'Disconnected with ' + ad[0] + ':' + str(ad[1]) + ' because the logger wants to leave directly.'
        print disp
        Global.log.write(disp + "\n")
        return (data, True)
    if data == "logout":
        connect.sendall("logout")
        disp = 'Disconnected with ' + ad[0] + ':' + str(ad[1]) + ' because the logger wants to logout from the Chatting room.'
        print disp
        Global.log.write(disp + "\n")
        return (data, True)
    if data == "timeout":
        disp = 'Disconnected with ' + ad[0] + ':' + str(ad[1]) + ' because timeout issue.'
        print disp
        Global.log.write(disp + "\n")
        return (data, True)
    if data == "serverstop":
        disp = 'Disconnected with ' + ad[0] + ':' + str(ad[1]) + ' because the server will stop due to some reasons (system error or administrator operation).'
        print disp
        Global.log.write(disp + "\n")
        # here we don't notify others because we all will logout nearly at the same time
        return (data, True)
    return (data, False)


def newuser_notif(name):
    #------------------------- broadcasting for each online user -----------------------------
    #if len(Global.list_user) != 0:
    for user in Global.list_user:
        if user.name != name:  # not broadcasting the message to himself
            message = Global.message("System(broadcast)", user.name, "\"" + name + "\"" + " has just logged in.")
            Global.message_rep[user.name].append(message)
            Global.event[user.name].set()
    disp = "New user \"" + name + "\" logging in notification has been sent!"
    print disp
    Global.log.write(disp + "\n")
    return


def levuser_notif(name):  # don't disclass different ways to leave for the clients
    #------------------------- broadcasting for each online user -----------------------------
    #if len(Global.list_user) != 0:
    for user in Global.list_user:
        if user.name != name:  # not broadcasting the message to himself
            message = Global.message("System(broadcast)", user.name, "\"" + name + "\"" + " has just logged out.")
            Global.message_rep[user.name].append(message)
            Global.event[user.name].set()
    disp = "User \"" + name + "\" logging out notification has been sent!"
    print disp
    Global.log.write(disp + "\n")
    return


def newuser_register(connect, ad):
    disp = "Someone on " + ad[0] + ':' + str(ad[1]) + " is trying to register a new user."
    print disp
    Global.log.write(disp + "\n")
    # double check for the user name sensitivity
    bol = True
    while bol:
        connect.sendall("Please enter your new user name:\n>>")
        #======================================
        (data, quit) = check_input(connect, ad)
        if quit:
            print "The client program on " + ad[0] + ':' + str(ad[1]) + " has quited due to some reasons (user quit or KeyboardInterupt)."
            connect.close()
            return quit
        #======================================
        if data in ["register", "de-register"]:  # sensitivity check
            connect.sendall("You should not use this sensitive word as your user name! The new user registration session will quit.\nPlease enter your username: (or you can \"quit\" or \"resigter\" or \"de-resigter\" by those commands)\n>>")
            disp = "The person on " + ad[0] + ':' + str(ad[1]) + " uses a sensitive term as his user-name, which is not permitted."
            print disp
            Global.log.write(disp + "\n")
            return
        elif data in Global.u_p:  # existing check
            connect.sendall("You should not use this existing name as your user name, please try again! The new user registration session will quit.\nPlease enter your username: (or you can \"quit\" or \"resigter\" or \"de-resigter\" by those commands)\n>>")
            disp = "The person on " + ad[0] + ':' + str(ad[1]) + " uses a existing name as his user-name, which is not permitted."
            print disp
            Global.log.write(disp + "\n")
            return
        else:
            bol = False
    new_user = data

    connect.sendall("Please enter your new password:\n>>")
    disp = "The person on " + ad[0] + ':' + str(ad[1]) + " uses \"" + new_user + "\" as his new_user name, and now he is typing his password."
    print disp
    Global.log.write(disp + "\n")
    #======================================
    (data, quit) = check_input_early(connect, ad)
    if quit:
        print "The client program on " + ad[0] + ':' + str(ad[1]) + " has quited due to some reasons (user quit or KeyboardInterupt)."
        connect.close()
        return quit
    #======================================
    new_pwd = data

    #---------------- double check the new password feasibility -------------------
    bol = True
    N = 0
    connect.sendall("Please re-enter your password:\n>>")
    while bol:
        N += 1
        disp = "The person on " + ad[0] + ':' + str(ad[1]) + " is re-typing his password for \"" + new_user + "\"."
        print disp
        Global.log.write(disp + "\n")
        #======================================
        (data, quit) = check_input(connect, ad)
        if quit:
            print "The client program on " + ad[0] + ':' + str(ad[1]) + " has quited due to some reasons (user quit or KeyboardInterupt)."
            connect.close()
            return quit
        #======================================
        if data != new_pwd:
            if N == 2:
                connect.sendall("It's not the same with your previous input pwd. The new user registration session will quit.\nPlease enter your username: (or you can \"quit\" or \"resigter\" or \"de-resigter\" by those commands)\n>>")
                disp = "The person on " + ad[0] + ':' + str(ad[1]) + " is re-typed an unconsistant password with his previous input for \"" + new_user + "\"."
                print disp
                Global.log.write(disp + "\n")
                return
            else:
                connect.sendall("It's not the same with your previous input pwd. You can have only another try.\nPlease re-enter your password:\n>>")
                disp = "The person on " + ad[0] + ':' + str(ad[1]) + " is re-typed an unconsistant password with his previous input for \"" + new_user + "\"."
                print disp
                Global.log.write(disp + "\n")
        else:
            bol = False
    Global.u_p[new_user]=new_pwd
    Global.update(new_user)
    connect.sendall("You have successfully registered \"" + new_user + "\". Please continue!\nPlease enter your username: (or you can \"quit\" or \"resigter\" or \"de-resigter\" by those commands)\n>>")
    disp = "New user \"" + new_user + "\" with password \"" + new_pwd + "\" has been successfully created on " + ad[0] + ':' + str(ad[1]) + "."
    print disp
    Global.log.write(disp + "\n")
    return False

def olduser_cancel(connect,ad, pwd_wrongnumber_rep):
    #----------------- check the feasibility of this user --------------------
    connect.sendall("Please enter your existing user name:\n>>")
    #======================================
    (data, quit) = check_input_early(connect, ad)
    if quit:
        print "The client program on " + ad[0] + ':' + str(ad[1]) + " has quited due to some reasons (user quit or KeyboardInterupt)."
        connect.close()
        return quit
    #======================================
    if data not in Global.u_p:
        connect.send("Username not existing. This de-registration session will quit, and you will go to the main log in session.\nPlease enter your username: (or you can \"quit\" or \"resigter\" or \"de-resigter\" by those commands)\n>>")
        disp = "Someone on " + ad[0] + ':' + str(ad[1]) + " is trying to cancel a user \"" + data + "\" but that user doesn't exist."
        print disp
        Global.log.write(disp + "\n")
        return False
    else:
        UNBLOCK = True
        #------ check blocking status ----------
        for i in Global.list_block:
            if ad[0] == i.ip and data == i.name:
                if i.get_bool():
                    connect.send("You are blocked! Please wait, this user has been blocked. You have " + str(i.get_leftover()) + " time left to try cancel this name on this machine again!\nPlease enter your username: (or you can \"quit\" or \"resigter\" or \"de-resigter\" by those commands)\n>>")
                    disp = "The user \"" + data + "\" on the ip address of \"" + i.ip + "\" want to cancel himself, but was blocked. It has " + str(i.get_leftover()) + " time left to perform cancelling this name again!"
                    print disp
                    Global.log.write(disp + "\n")
                    return False
                else:
                    Global.list_block.remove(i)
                    pwd_wrongnumber_rep[data] = 0
                    break
        #------ check logging status ----------
        for i in Global.list_user:
            if data == i.name:
                connect.send("The present user is logging in right now. So you can't cancel it. This session will quit and you will turn to the main login session.\nPlease enter your username: (or you can \"quit\" or \"resigter\" or \"de-resigter\" by those commands)\n>>")
                disp = "The user \"" + data + "\" actually has logged in. But another one want to cancel this user name, which is not permitted. Its IP address and port are \"" + ad[0] + ':' + str(ad[1]) +"\"."
                print disp
                Global.log.write(disp + "\n")
                return False
    exist_user = data

    #------------------ check the password (bring the 3-times blocking process)----------------------
    connect.sendall("Please enter your password:\n>>")
    #======================================
    (data, quit) = check_input(connect, ad)
    if quit:
        print "The client program on " + ad[0] + ':' + str(ad[1]) + " has quited due to some reasons (user quit or KeyboardInterupt)."
        connect.close()
        return True
    #======================================
    pwd = data.strip()
    pwd_real = Global.u_p[exist_user]  # I will set the directory later on to form a repository

    #---------------------- password verification module --------------------------
    if pwd != pwd_real:
        if exist_user in pwd_wrongnumber_rep:
            pwd_wrongnumber_rep[exist_user] += 1
        else:
            pwd_wrongnumber_rep[exist_user] = 1
        if pwd_wrongnumber_rep[exist_user] == 3:
            connect.sendall("Wrong password for 3 times for this user on this machine in this logging in session. You are blocked. Please try with this user after " + str(Global.BLOCK_TIME) + " seconds. Or you can try another user in this machine.\nPlease enter your username: (or you can \"quit\" or \"resigter\" or \"de-resigter\" by those commands)\n>>")
            disp = "Wrong pwd 3 times for user \"" + exist_user + "\" on " + ad[0] + ':' + str(ad[1])
            print disp
            Global.log.write(disp + "\n")
            block = Global.block(ad[0], time.time(), exist_user)
            Global.list_block.append(block)
            return False
        else:
            connect.send('Wrong password for this user! You have ' + str(3-pwd_wrongnumber_rep[exist_user]) + ' times to give another try for this user on this machine in this connection session!\nPlease enter your username: (or you can \"quit\" or \"resigter\" or \"de-resigter\" by those commands)\n>>')
            disp = 'Wrong password for \"' + exist_user + '\" on ' + ad[0] + ':' + str(ad[1]) + '. There are ' + str(3-pwd_wrongnumber_rep[exist_user]) + ' times left to give another try for this user!'
            print disp
            Global.log.write(disp + "\n")
            return False
    exist_pwd = pwd

    #---------------- make sure to delete ---------------
    connect.sendall("Password verified. Are you sure to cancel your registration for " + exist_user + "? Enter \"yes\" or \"no\":\n>>")
    disp = 'User \"' + exist_user + '\" on ' + ad[0] + ':' + str(ad[1]) + ' has passed the PWD verification during the cancellation process. Now he is making sure that he will cancel this account!'
    print disp
    Global.log.write(disp + "\n")
    bol = True
    N = 0
    while bol:
        N += 1
        #======================================
        (data, quit) = check_input(connect, ad)
        if quit:
            print "The client program on " + ad[0] + ':' + str(ad[1]) + " has quited due to some reasons (user quit or KeyboardInterupt)."
            connect.close()
            return True
        #======================================
        if data not in ["yes", "no"]:
            if N == 2:
                connect.sendall("Sorry you did not enter \"yes\" or \"no\". This user de-registration session will quit, and you will turn to the main login session.\nPlease enter your username: (or you can \"quit\" or \"resigter\" or \"de-resigter\" by those commands)\n>>")
                return False
            else:
                connect.sendall("Please re-enter \"yes\" or \"no\". You can have another try.\n>>")
        else:
            bol = False
    if data == "yes":
        del Global.u_p[exist_user]
        Global.de_update(exist_user)
        connect.sendall("You have successfully cancelled \"" + exist_user + "\". Please continue!\nPlease enter your username: (or you can \"quit\" or \"resigter\" or \"de-register\" by those commands)\n>>")
        disp = "New user \"" + exist_user + "\" with password \"" + exist_pwd + "\" has been successfully cancelled on " + ad[0] + ':' + str(ad[1]) + "."
        print disp
        Global.log.write(disp + "\n")
    else:
        connect.sendall("You don't cancel \"" + exist_user + "\". Please continue!\nPlease enter your username: (or you can \"quit\" or \"resigter\" or \"de-register\" by those commands)\n>>")
        disp = "New user \"" + exist_user + "\" with password \"" + exist_pwd + "\" has not been successfully cancelled on " + ad[0] + ':' + str(ad[1]) + "."
        print disp
        Global.log.write(disp + "\n")
    return False


def client(connect, ad):
    #-------------------- deal with the maximum user problem first ------------------------
    Global.lock_con.acquire()
    if Global.con >= Global.MaxCon:
        Global.lock_con.release()
        # it's safer that each time we just send one message to the receiver
        connect.send("maxuser. The connection has arrived its maximum " \
                    "value " + str(Global.MaxCon) + ", please wait a moment " \
                    "for others log-out and then log-in later on\n")
        disp = 'Disconnected with ' + ad[0] + ':' + str(ad[1]) + ' due to maximum user problem'
        print disp
        Global.log.write(disp + "\n")
        connect.close()
        return
    Global.lock_con.release()

    #Sending message to connected client
    connect.send('Now you are trying to connect to the Chatting room! You should log in first. Type required information and hit enter!\n' + 'Please enter your username: (or you can \"quit\" or \"resigter\" or \"de-resigter\" by those commands)\n')
    disp = "The server session openning information has been sent"
    print disp
    Global.log.write(disp + "\n")

    #---------------------- login check or (de-)register (<username>-<password>, "quit", "termination", "(de-)register")------------------------
    pwd_wrongnumber_rep = {}  # store the number of wrong pwd entering for a specific user; initialize as empty for each new connection session
    while 1:  # only the user has successfully logged in this loop can terminate; or quit this loop, directly return
        #=======================================
        # safely read data from the client, and check whether the
        # priority operation exists ("logout", "quit", "termination")
        (name, quit) = check_input_early(connect, ad)
        if quit:
            connect.close()
            return
        #=======================================

        #-------------------- new user registration ----------------------
        if name == "register":
            quit = newuser_register(connect, ad)
            if quit:
                return
            continue

        #-------------------- old user cancellation ----------------------
        if name == "de-register":
            quit = olduser_cancel(connect, ad, pwd_wrongnumber_rep)
            if quit:
                return
            continue

        #--------------------- user not existing --------------------------
        elif name not in Global.u_p:
            try:  # to capture the client windows closing broken pipe error ("" will be sent here, but the connection has been broken, so there will be errors)
                connect.sendall("Username not existing.. Please type again:\n>>")
            except:
                disp1 = "Some errors happened in the client side, because the host can't receive the data normally!" + "\n"
                disp2 = "Maybe the user directly close the running terminal windows!\n"
                disp3 = "This server-client interaction thread will terminate right now!" + "\n"
                disp4 = 'Disconnected with ' + ad[0] + ':' + str(ad[1]) + ' because some errors happened in the client side.'
                disp = disp1 + disp2 + disp3 + disp4
                print disp
                Global.log.write(disp + "\n")
                return
            disp = "The logging user name is \"" + name + "\" on: " + ad[0] + ':' + str(ad[1]) + ". The user-name not existing notification has been sent!"
            print disp
            Global.log.write(disp + "\n")
            continue

        #--------------------- check blocking and online status, if no problem, continue checking pwd ---------------------
        else:
            bol = False
            for i in Global.list_block:
                if ad[0] == i.ip and name == i.name:
                    if i.get_bool():
                        connect.send("You are blocked! Please wait, you have " + str(i.get_leftover()) + " time left to log in using this name again!\nYou can try another user:\n>>")
                        disp = "The user \"" + name + "\" on the ip address of \"" + i.ip + "\" want to log in, but was blocked. It has " + str(i.get_leftover()) + " time left to log in using this name again!"
                        print disp
                        Global.log.write(disp + "\n")
                        bol = True
                        break
                    else:
                        Global.list_block.remove(i)
                        pwd_wrongnumber_rep[name] = 0  # but if it has been removed from the list_block, then we did not reset this value to 0
                        break
            if bol:
                continue
            for i in Global.list_user:
                if name == i.name:
                    connect.send("The present user is being logged in. Please use another user to log-in:\n>>")
                    disp = "The user \"" + name + "\" actually has logged in. But another one also want to log in using this user-name. Its IP address and port are \"" + ad[0] + ':' + str(ad[1]) +"\"."
                    print disp
                    Global.log.write(disp + "\n")
                    bol = True
                    break
            if bol:
                continue

            # by now this user with this "name" can log in; check pwd now
            #---------------------- check pwd for the normally login ------------------------
            connect.sendall('Please enter your password:\n>>')
            disp = "The user \"" + name + "\" on \"" + ad[0] + ':' + str(ad[1]) + "\" is trying to log in. Now he is typing the password..."
            print disp
            Global.log.write(disp + "\n")
            #======================================
            (data, quit) = check_input_early(connect, ad)  # <username>, <password>, "quit", "termination", "(de-)register"
            if quit:
                connect.close()
                return
            #======================================
            pwd = data.strip()
            pwd_real = Global.u_p[name]  # I will set the directory later on to form a repository

            #---------------------- password verification module --------------------------
            if pwd != pwd_real:
                if name in pwd_wrongnumber_rep:
                    pwd_wrongnumber_rep[name] += 1
                else:
                    pwd_wrongnumber_rep[name] = 1
                if pwd_wrongnumber_rep[name] == 3:
                    connect.sendall("Wrong password for 3 times. You are blocked. Please try to log-in with this user after " + str(Global.BLOCK_TIME) + " seconds. Or you can try another user in this machine.\n>>")
                    disp = "Wrong pwd 3 times for user \"" + name + "\" on " + ad[0] + ':' + str(ad[1])
                    print disp
                    Global.log.write(disp + "\n")
                    block = Global.block(ad[0], time.time(), name)
                    Global.list_block.append(block)
                else:
                    connect.send('Wrong password! You have ' + str(3-pwd_wrongnumber_rep[name]) + ' times to give another try for this user on this machine in this connection session!\nPlease enter your username:\n>>')
                    disp = 'Wrong password for \"' + name + '\" on ' + ad[0] + ':' + str(ad[1]) + '. There are ' + str(3-pwd_wrongnumber_rep[name]) + ' times left to give another try for this user!'
                    print disp
                    Global.log.write(disp + "\n")
            else:
                connect.sendall("logsuccess" + "Welcome to the Chatting room user \"" + name + "\"! Now you have successfully logged in!" + "\n" + name + ">>" + "@@@" + name)
                break

    ##============================ client-server interaction from here ===============================
    disp = "User \"" + name + "\" has successfully logged in on " + ad[0] + ':' + str(ad[1]) + "."
    print disp
    Global.log.write(disp + "\n")

    #-------------------- deal with the maximum user problem again -------------------------
    #------ because the MaxCon number may reached just during this user is logging in-------
    Global.lock_con.acquire()
    if Global.con >= Global.MaxCon:
        Global.lock_con.release()
        # it's safer that each time we just send one message to the receiver
        connect.send("maxuser. I'm sorry. Although you have passed the password verification, there already exist maximum number users online. The connection has arrived its maximum " \
                    "value " + str(Global.MaxCon) + ", please wait a moment " \
                    "for others log-out and then log-in later on.\n")
        disp = 'Disconnected with ' + ad[0] + ':' + str(ad[1]) + ' due to maximum user problem'
        print disp
        Global.log.write(disp + "\n")
        connect.close()
        return
    Global.lock_con.release()

    Global.lock_con.acquire()
    Global.con += 1
    Global.lock_con.release()
    user = Global.user(ad[0], ad[1], name)
    Global.list_user.append(user)

    # add a new feature: new user logging in notification
    newuser_notif(name)  # himself not yet added to the present user_list

    #DEBUG, but actually useful
    print "The present active users list:"
    print Global.list_user

    #--------- open the interaction thread ------------
    new_thread = threading.Thread(target=server_receiver, args=(connect, ad, name, user))
    new_thread.setDaemon(True)
    new_thread.start()

    #----------------------- open the server sender thread -------------------
    new_thread = threading.Thread(target=server_sender, args=(connect, ad, name))
    new_thread.setDaemon(True)
    new_thread.start()

    #------------------- here we have a TIME_OUT loop detection -------------------------
    Global.list_lastop[name] = time.time()  # default as an empty directory
    present_time = time.time()
    while True:  # TODO data concurrency here
        if present_time - Global.list_lastop[name] < Global.TIME_OUT:  # only under this circumstance we should go-on
            #------- by adding this we can log out this thread after the receiver thread has logged out -----
            if Global.TIME_OUT - (present_time - Global.list_lastop[name]) < Global.TIME_OUT_CHECK:
                waiting_time = Global.TIME_OUT - (present_time - Global.list_lastop[name])
            else:  # for fear that this thread should quit, or the TIME_OUT has been changed to a new value
                waiting_time = Global.TIME_OUT_CHECK
            #------------------------------------------------------------------------------------------------
            time.sleep(waiting_time)
            present_time = time.time()
            #--------- check whether this thread should exits here --------
            if user not in Global.list_user:
                del Global.list_lastop[name]
                return
            #-----------------------------
        else:
            connect.sendall("timeout" + str(Global.TIME_OUT))
            del Global.list_lastop[name]
            disp = "The present user \"" + name + "\" on " + ad[0] + ':' + str(ad[1]) + " has been automatically logged out due to time_out issue."
            print disp
            Global.log.write(disp + "\n")
            return