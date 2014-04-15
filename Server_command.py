import Global
import time
import os

def str_op_done(op, name):
    #return "The server has performed the \"" + op + "\" operation for you!" + "\n"  + name + ">>"
    return name + ">>"
           #"Please continue with the following commands:" + "\n" + Global.CONNECT.strip() + "\n"  + name + ">>\n"

def str_op_done_sys(op, name, ad):
    return "System has finished the operation \"" + op + "\" for user \"" + name + "\" on " + ad[0] + ':' + str(ad[1]) + "."

def str_check_format_con(format, op, name):
    s1="You should follow the format of \"" + format + "\" for the \"" + op + "\" command. Please try again!.." + "\n"  + name + ">>"
    #s2="Please continue with the following commands: " + "\n" + Global.CONNECT.strip() + "\n" + name + ">>"
    return s1

def command_res(connect, data, name, ad):
    #supported commands: "whoelse", "wholasthr", "broadcast", "message", "block", "unblock", "logout"
    if data[0] == "whoelse":  # I don't check the format of this command, because other words will be dropped.
        reply="The other users are:\n"
        N = 0
        for user in Global.list_user:
            if user.name != name:
                reply = reply + user.name + "\n"
                N += 1
        if N == 0:
            reply = reply + "There are no other users."
        reply=reply.strip()
        connect.sendall(reply + "\n")
        connect.sendall(str_op_done(data[0], name))
        disp = str_op_done_sys(data[0], name, ad)
        print disp
        Global.log.write(disp + "\n")
        return


    if data[0] == "message":
        #----------- preparing the data as "message" command format, and check the format at the same time -------------
        if len(data) >1:
            t1=data[0]  # temporary command
            t2=data[1]  # temporary receiver
            del data[0:2]
            t3=""  # temporary content
            for i in data:
                t3=t3+i+" "
            t3=t3.strip()
            if t3 == "":
                data = [t1, t2]
                connect.sendall(str_check_format_con("message <user> <message>", data[0], name))
                return
            else:
                data = [t1, t2, t3]
        else:
            connect.sendall(str_check_format_con("message <user> <message>", data[0], name))
            return

        #----------- check self message which should be avoided -------------
        if data[1] == name:
            connect.sendall("You should not send messages to yourself. Please try another one.." + "\n" + name + ">>")
            #connect.sendall("Please continue with the following commands: " + "\n" + Global.CONNECT.strip() + "\n" + name + ">>")
            return

        #----------- check whether the targetting user exists -------------
        if data[1] not in Global.u_p:
            connect.sendall("You surely keep the format of \"message\" command, but we can't find the targetting <user> in our database. You should try again!.." + "\n" + name + ">>")
            #connect.sendall("Please continue with the following commands: " + "\n" + Global.CONNECT.strip() + "\n" + name + ">>")
            return

        #------------------------- block check -----------------------------
        if data[1] in Global.block_rep[name]:
            connect.sendall("You cannot send any message to " + data[1] + ". You have been blocked by the user.\nPlease try another one to send message!.." + "\n"  + name + ">>")
            #connect.sendall("Please continue with the following commands: " + "\n" + Global.CONNECT.strip() + "\n" + name + ">>")
            return

        message = Global.message(name + "(private)", data[1], data[2])
        Global.message_rep[data[1]].append(message)
        #------------------------- check whether the targetting user is online or not -----------------------------
        bol=False
        for user in Global.list_user:
            if user.name == data[1]:
                bol = True
                break
        if bol:
            Global.event[data[1]].set()
            #connect.sendall("\n")
            connect.sendall(str_op_done(data[0], name))
            disp1 = str_op_done_sys(data[0], name, ad) + "\n"
            disp2 = "The receiver is \"" + data[1] + "\" and the content is \"" + data[2] + "\" and the sender's ip is " + ad[0] + ':' + str(ad[1]) + "."
            disp =disp1 + disp2
            print disp
            Global.log.write(disp + "\n")
            return
        else:
            #connect.sendall("\n")
            connect.sendall("The user \"" + data[1] + "\" is unfortunately not online. But the server has stored your message.\n")
            connect.sendall(str_op_done("off-line "+data[0], name))
            disp1 = str_op_done_sys("off-line " + data[0], name, ad) + "\n"
            disp2 = "The receiver is \"" + data[1] + "\" and the content is \"" + data[2] + "\" and the sender's ip is " + ad[0] + ':' + str(ad[1]) + "."
            disp = disp1 + disp2
            print disp
            Global.log.write(disp + "\n")
            return


    if data[0] == "wholasthr":
        l=[]
        for user in Global.list_user:
            if user.name != name:
                l.append(user.name)
        for user in Global.lasthr_rep:
            if Global.lasthr_rep[user] != None:
                if user not in l:
                    if time.time() - Global.lasthr_rep[user] < Global.LAST_HOUR:
                        l.append(user)
        s='\n'.join(l)
        reply="The wholasthr users are:\n" + s
        connect.sendall(reply + "\n")
        connect.sendall(str_op_done(data[0], name))
        disp = str_op_done_sys(data[0], name, ad)
        print disp
        Global.log.write(disp + "\n")
        return


    if data[0] == "broadcast":  # TODO we don't do the block check for the broadcasting
        #----------- preparing the data as "broadcast" command format, and check the format at the same time -------------
        if len(data) >1:
            t1=data[0]  # temporary command
            del data[0:1]
            t2=""  # temporary content
            for i in data:
                t2=t2+i+" "
            t2=t2.strip()
            if t2=="":
                connect.sendall(str_check_format_con("broadcast <message>", data[0], name))
                return
            else:
                data = [t1, t2]
        else:
            connect.sendall(str_check_format_con("broadcast <message>", data[0], name))
            return

        #------------------------- broadcasting for each online user -----------------------------
        for user in Global.u_p:
            message = Global.message(name+"(broadcast)", user, data[1])
            Global.message_rep[user].append(message)
            bol=False  # check whether that user is online or not
            for user_obj in Global.list_user:
                if user_obj.name == user:
                    bol = True
                    break
            if bol:  # online users
                Global.event[user].set()
        disp1 = str_op_done_sys(data[0], name, ad) + "\n"
        disp2 = "The Content is \"" + data[1] + "\" and the sender's ip is " + ad[0] + ':' + str(ad[1]) + "."
        disp = disp1 + disp2
        print disp
        Global.log.write(disp + "\n")
        return


    if data[0] == "block":
        #----------- preparing the data as "block" command format, and check the format at the same time -------------
        if len(data) != 2:
            connect.sendall(str_check_format_con("block <user>", data[0], name))
            return

        #----------- check whether the targetting user exists -------------
        if data[1] not in Global.u_p:
            connect.sendall("You surely keep the format of \"block\" command, but we can't find the targetting <user> in our database. You should try again!.." + "\n"  + name + ">>")
            #connect.sendall("Please continue with the following commands: " + "\n" + Global.CONNECT.strip() + "\n" + name + ">>")
            return

        #----------- self-block check ---------------
        if data[1] == name:
            connect.sendall("Error! You cannot block yourself! Please try again!.." + "\n"  + name + ">>")
            #connect.sendall("Please continue with the following commands: " + "\n" + Global.CONNECT.strip() + "\n" + name + ">>")
            return

        #----------- second-block check ---------------
        if name in Global.block_rep[data[1]]:
            connect.sendall("You have blocked this guy. Why do you block again? Please try again!.." + "\n"  + name + ">>")
            #connect.sendall("Please continue with the following commands: " + "\n" + Global.CONNECT.strip() + "\n" + name + ">>")
            return

        Global.block_rep[data[1]].append(name)
        connect.sendall("You have successfully blocked " + data[1] + " from sending you messages.\n")
        connect.sendall(str_op_done(data[0], name))
        disp1 = str_op_done_sys(data[0], name, ad) + "\n"
        disp2 = "He has successfully blocked \"" + data[1] + "\"."
        disp = disp1 + disp2
        print disp
        Global.log.write(disp + "\n")
        return


    if data[0] == "unblock":
        #----------- preparing the data as "unblock" command format, and check the format at the same time -------------
        if len(data) != 2:
            connect.sendall(str_check_format_con("block <user>", data[0], name))
            return

        #----------- check whether the targetting user exists -------------
        if data[1] not in Global.u_p:
            connect.sendall("You surely keep the format of \"block\" command, but we can't find the targetting <user> in our database. You should try again!.." + "\n"  + name + ">>")
            #connect.sendall("Please continue with the following commands: " + "\n" + Global.CONNECT.strip() + "\n" + name + ">>")
            return

        if data[1] == name:
            connect.sendall("You surely keep the format of \"block\" command, but as you can't block yourself, there is no probability that you can unblock yourself!.." + "\n"  + name + ">>")
            #connect.sendall("Please continue with the following commands: " + "\n" + Global.CONNECT.strip() + "\n" + name + ">>")
            return

        #---------- check whether the target has been blocked -------------
        if name not in Global.block_rep[data[1]]:
            connect.sendall("You try to unblock an unblocked object. Please make another meaningful try." + "\n"  + name + ">>")
            #connect.sendall("Please continue with the following commands: " + "\n" + Global.CONNECT.strip() + "\n" + name + ">>")
            return

        Global.block_rep[data[1]].remove(name)
        connect.sendall("You have successfully unblocked " + data[1] + "\n")
        connect.sendall(str_op_done(data[0], name))
        disp1 = str_op_done_sys(data[0], name, ad) + "\n"
        disp2 = "He has successfully unblocked " + data[1] + "."
        disp =disp1 + disp2
        print disp
        Global.log.write(disp + "\n")
        return


    if data[0] == "file":
        #----------- preparing the data as "message" command format, and check the format at the same time -------------
        if len(data) >1:
            t1=data[0]  # temporary command
            t2=data[1]  # temporary receiver
            del data[0:2]
            t3=""  # temporary content
            for i in data:
                t3=t3+i+" "
            t3=t3.strip()
            if t3 == "":
                data = [t1, t2]
                connect.sendall(str_check_format_con("file <receiver> <filename>", data[0], name))
                return
            else:
                data = [t1, t2, t3]
        else:
            connect.sendall(str_check_format_con("file <receiver> <filename>", data[0], name))
            return

        #----------- check whether the targetting user exists -------------
        if data[1] not in Global.u_p:
            connect.sendall("You surely keep the format of \"message\" command, but we can't find the targetting <user> in our database. You should try again!.." + "\n"  + name + ">>")
            #connect.sendall("Please continue with the following commands: " + "\n" + Global.CONNECT.strip() + "\n" + name + ">>")
            return

        #------------------------- block check -----------------------------
        if data[1] in Global.block_rep[name]:
            connect.sendall("You have been blocked by this user! I'm sorry but please try another one!.." + "\n"  + name + ">>")
            #connect.sendall("Please continue with the following commands: " + "\n" + Global.CONNECT.strip() + "\n" + name + ">>")
            return

        if (name, data[2].strip()) not in Global.file_rep[data[1]]:
            Global.file_rep[data[1]].append((name, data[2]))
            #DEBUG
            #print data[1]+data[2]
        connect.sendall("filetransfer " + name + " " + data[1] + " " + data[2])  # filetransfer  sender receiver filename
        disp1 = "The system has received the file transfer request from " + data[0] + "\n"
        disp2 = "The receiver is \"" + data[1] + "\" and the filename is \"" + data[2] + "\" and the sender's ip is " + ad[0] + ':' + str(ad[1]) + "."
        disp =disp1 + disp2
        print disp
        Global.log.write(disp + "\n")
        return

    if data[0] == "filetransferdec":  # the client can't find that file
        Global.file_rep[data[2]].remove((data[1], data[3]))
        #connect.sendall("Please continue with the following commands: " + "\n" + Global.CONNECT.strip() + "\n" + name + ">>")
        connect.sendall(name + ">>")
        disp = "The client can't find that file. He may try again."
        print disp
        Global.log.write(disp + "\n")
        return


    if data[0] == "filetransfer":
        # TODO remember to block the server sender thread (I tried it and found that there is no need actually)
        disp = "Now user \"%s\" begins to transfer \"%s\" to user \"%s\"" %(data[1], data[3], data[2])
        print disp
        Global.log.write(disp + "\n")
        #---------
        predir = os.getcwd()
        f = open(predir + '/' + data[1] + "_" + data[2] + "_" + data[3], 'wb')  # b means binary method write
        connect.send('ready')
        while True:
            dat = connect.recv(4096)
            if dat == 'EOF':
                disp = "server receive file success!"
                print disp
                Global.log.write(disp + "\n")
                break
            f.write(dat)
        f.close()
        #---------
        disp = "Now user \"%s\" has succeeded to transfer \"%s\" to user \"%s\"" %(data[1], data[3], data[2])
        print disp
        Global.log.write(disp + "\n")
        connect.sendall("file \"" + data[3] + "\" has been successfully received by the server." + "\n" + name + ">>")
        #connect.sendall("Please continue with the following commands: " + "\n" + Global.CONNECT.strip() + "\n" + name + ">>")

        message = Global.message(data[1] + "(file_transfer)", data[2], data[3])
        Global.message_rep[data[2]].append(message)
        #------------------------- check whether the targetting user is online or not -----------------------------
        bol=False
        for user in Global.list_user:
            if user.name == data[2]:
                bol = True
                break
        if bol:
            Global.event[data[2]].set()
            return


    if data[0] == "fileget":
        #----------- preparing the data as "message" command format, and check the format at the same time -------------
        if len(data) >1:
            t1=data[0]  # temporary command
            t2=data[1]  # temporary receiver
            del data[0:2]
            t3=""  # temporary content
            for i in data:
                t3=t3+i+" "
            t3=t3.strip()
            if t3 == "":
                data = [t1, t2]
                connect.sendall(str_check_format_con("fileget <source> <filename>", data[0], name))
                return
            else:
                data = [t1, t2, t3]
        else:
            result = ""
            for t in Global.file_rep[name]:
                result = result + "File \"%s\" from \"%s\"." %(t[1],t[0]) + "\n"
            if len(Global.file_rep[name]) == 0:
                connect.sendall("No files for you. Please continue.\n" + name + ">>")
                disp = "Successfully perform the \"fileget\" operation."
                print disp
                Global.log.write(disp + "\n")
                return
            result = result + name + ">>"
            connect.sendall(result)
            disp = "Successfully perform the \"fileget\" operation."
            print disp
            Global.log.write(disp + "\n")
            return

        #----------- check whether the targetting source exists -------------
        if data[1] not in Global.u_p:
            connect.sendall("You surely keep the format of \"fileget\" command, but we can't find the targetting <source> in our database. You should try again!.." + "\n" + name + ">>")
            #connect.sendall("Please continue with the following commands: " + "\n" + Global.CONNECT.strip() + "\n" + name + ">>")
            return

        #----------- check whether the targetting file exists -------------
        if (data[1], data[2]) not in Global.file_rep[name]:
            connect.sendall("You surely keep the format of \"fileget\" command, but we can't find the targetting <filename> in our database. You should try again!.." + "\n" + name + ">>")
            #connect.sendall("Please continue with the following commands: " + "\n" + Global.CONNECT.strip() + "\n" + name + ">>")
            return

        # TODO check whether the file exists; this kind of thing should not happen here!! are you joking?! we are the server builder!!
        # TODO blocking another event signal (must)
        Global.lock[name].acquire()
        disp = "starting send file!"
        print disp
        Global.log.write(disp + "\n")
        connect.send("file_ready " + data[1] + " " + data[2])  # the ready to send signal for the client
        time.sleep(1)
        predir = os.getcwd()
        f = open(predir + '/' + data[1] + "_" + name + "_" + data[2], 'rb')  # b means binary method write
        reply = connect.recv(1024)
        if reply == "ready":
            while True:
                dat = f.read(4096)
                if not dat:
                    break
                connect.send(dat)
            f.close()
            time.sleep(1)
            connect.sendall('EOF')
            disp = "send file success!"
            print disp
            Global.log.write(disp + "\n")
            Global.file_rep[name].remove((data[1], data[2]))

            #----------------- remove the stored file in the server -------------------
            predir = os.getcwd()
            try:
                os.remove(predir+'/' + data[1] + "_" + name + "_" + data[2])
            except:
                disp = "Some errors happen during the file deletion process."
                print disp
                Global.log.write(disp + "\n")
                connect.sendall("Some errors happen during the file deletion process.")
                return

            connect.sendall(name + ">>")  # TODO the just unblocked lock will send message and there will not be "\n", like: Columbia>>Google(private): try~
            Global.lock[name].release()
            #connect.sendall("Please continue with the following commands: " + "\n" + Global.CONNECT.strip() + "\n" + name + ">>")
            return

        else:
            disp = "The client doesn't give a ready to receive signal!"
            print disp
            Global.log.write(disp + "\n")
            Global.lock[name].release()
            return


    if data[0] == "filedecline":
        #----------- preparing the data as "message" command format, and check the format at the same time -------------
        if len(data) >1:
            t1=data[0]  # temporary command
            t2=data[1]  # temporary receiver
            del data[0:2]
            t3=""  # temporary content
            for i in data:
                t3=t3+i+" "
            t3=t3.strip()
            if t3 == "":
                data = [t1, t2]
                connect.sendall(str_check_format_con("filedecline <source> <filename>", data[0], name))
                return
            else:
                data = [t1, t2, t3]
        else:
            connect.sendall(str_check_format_con("filedecline <source> <filename>", data[0], name))
            return

        #----------- check whether the targetting source exists -------------
        if data[1] not in Global.u_p:
            connect.sendall("You surely keep the format of \"filedecline\" command, but we can't find the targetting <source> in our database. You should try again!.." + "\n" + name + ">>")
            #connect.sendall("Please continue with the following commands: " + "\n" + Global.CONNECT.strip() + "\n" + name + ">>")
            return

        #----------- check whether the targetting file exists -------------
        if (data[1], data[2]) not in Global.file_rep[name]:
            connect.sendall("You surely keep the format of \"filedecline\" command, but we can't find the targetting <filename> in our database. You should try again!.." + "\n" + name + ">>")
            #connect.sendall("Please continue with the following commands: " + "\n" + Global.CONNECT.strip() + "\n" + name + ">>")
            return

        Global.file_rep[name].remove((data[1], data[2]))
        predir = os.getcwd()
        try:
            os.remove(predir+'/' + data[1] + "_" + name + "_" + data[2])
        except:
            disp = "Some errors happen during the file deletion process."
            print disp
            Global.log.write(disp + "\n")
            connect.sendall("Some errors happen during the file deletion process.")
            return

        connect.sendall("Successfully perform the \"filedecline\" operation for you. Delete \"" + data[2] + "\" from \"" + data[1] + "\"." + "\n" + name + ">>")
        disp = "Successfully perform the \"filedecline\" operation for user %s. Delete \"%s\" from \"%s\"." %(name,data[2],data[1])
        print disp
        Global.log.write(disp + "\n")
        #connect.sendall("Please continue with the following commands: " + "\n" + Global.CONNECT.strip() + "\n" + name + ">>")
        return