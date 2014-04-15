#Global variable declaration and assignment
import time
import os
import threading
import socket


class block:  # a class for blocking a user due to 3 times wrong password entering

    def __init__(self, ip, t, name):
        self.ip = ip
        self.start = t
        self.name = name

    def get_leftover(self):
        return BLOCK_TIME - time.time() + self.start

    def get_bool(self):
        return self.get_leftover() > 0

class user:  # used to constructed the present existing user list

    def __init__(self, ip, port, name):
        self.ip = ip  # string
        self.port = port  # number
        self.name = name  # string

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.__str__()

class message:  # used to store all the private or broadcast message
                # if it is a private message, the sender will be "xxx(private)"
                # if it is a broadcast message, the sender will be "xxx(broadcast)"
                # if it is a new_user log-in or log-out notification message, the sender will be "System(broadcast)"
                # if the message is "System: serverstop", it means that the server is stopping, and this kind of message
                #        is used to terminate this sending thread of a server's connection
                # if the message is "System: logout", it means that the user want to "logout" or "quit" or closing window
                #        interupt, and this message is used to terminate this sending thread of a server's connection
    def __init__(self, sender, receiver, content):
        self.sender = sender
        self.receiver = receiver
        self.content = content

def get_u_p():  # get the user-password directory from the outside file
    u_p={}
    predir = os.getcwd()
    file = open(predir+'/'+'user_pass.txt','r')
    lines = file.readlines()
    for line in lines:
        unit=(line.strip()).split(" ")
        u_p[unit[0]]=unit[1]
    file.close()
    return u_p

def get_para():  # get the "MaxCon; BLOCK_TIME; LAST_HOUR; TIME_OUT" from the outside file
    d_t={}
    predir = os.getcwd()
    file = open(predir+'/'+'para.txt','r')
    lines = file.readlines()
    for line in lines:
        unit=(line.strip()).split(" ")
        d_t[unit[0]]=unit[1]
    file.close()
    MaxCon = int(d_t["MaxCon"])
    BLOCK_TIME = float(d_t["BLOCK_TIME"])  # in seconds
    #LAST_HOUR = float(d_t["LAST_HOUR"]) * 60 * 60  # in hour, so should multiply 60 * 60
    #TIME_OUT = float(d_t["TIME_OUT"]) * 60  # in minutes, so should multiply 60
    LAST_HOUR = float(d_t["LAST_HOUR"])  # in seconds, for testing convenience
    TIME_OUT = float(d_t["TIME_OUT"])  # in seconds, for testing convenience
    #print MaxCon,
    #print type(MaxCon)
    #print BLOCK_TIME,
    #print type(BLOCK_TIME)
    #print LAST_HOUR,
    #print type(LAST_HOUR)
    #print TIME_OUT,
    #print type(TIME_OUT)
    return (MaxCon, BLOCK_TIME, LAST_HOUR, TIME_OUT)

def save_para(MaxCon, BLOCK_TIME, LAST_HOUR, TIME_OUT):  # save the changed parameters after the server stop
    predir = os.getcwd()
    file = open(predir+'/'+'para.txt','w')
    file.write("MaxCon " + str(MaxCon) + "\n")
    file.write("BLOCK_TIME " + str(BLOCK_TIME) + "\n")
    #file.write("LAST_HOUR " + str(LAST_HOUR/3600) + "\n")
    #file.write("TIME_OUT " + str(TIME_OUT/60) + "\n")
    file.write("LAST_HOUR " + str(LAST_HOUR) + "\n")
    file.write("TIME_OUT " + str(TIME_OUT) + "\n")
    file.close()
    return

def save_u_p():  # save the new user-password directory to the file outside each time we log out
    predir = os.getcwd()
    file = open(predir+'/'+'user_pass.txt','w')
    for user in u_p:
        file.write(user + " " + u_p[user] + "\n")
    file.close()
    return

def initial_event(u_p):  # initialize the event directory, default as event.clear()
    dir = {}
    for user in u_p:
        dir[user] = threading.Event()
        dir[user].clear()
    return dir

#-------------------- message_rep related operation ----------------------
def initial_message(u_p, message):  # initialize the message directory (actually the message database), as empty at the beginning
    message_rep = {}
    for user in u_p:
        message_rep[user] = []
    predir = os.getcwd()
    file = open(predir+'/'+'message_rep.txt','r')
    lines = file.readlines()
    file.close()
    for line in lines:
        unit=line.strip()
        if unit == "":
            break
        unit = unit.split(" ")  # xxx xxx xxx xxx each line
        object = message(unit[1], unit[2], " ".join(unit[3:]))
        message_rep[unit[0]].append(object)
    return message_rep

def save_message_rep():
    """
    self.sender = sender
    self.receive = receiver
    self.content = content
    """
    predir = os.getcwd()
    file = open(predir+'/'+'message_rep.txt','w')
    for user in message_rep:
        for message in message_rep[user]:
            if message.sender != "System":  # during test I find that the "System: serverstop" message maybe stored, so here check it
                file.write(user + " " + message.sender + " " + message.receiver + " " + message.content + "\n")
    file.close()
    return
#----------------------------------------------------------------------

def get_lasthr(u_p):  # initialize the last-time logging-out information for each user, as "None" at the beginning
    dir = {}
    for user in u_p:
        dir[user] = None
    return dir

#-------------------- block_rep related operation ----------------------
def get_block(u_p):  # initialize the block list for each user, as empty at the beginning; the key is blocked user
    block_rep = {}
    for user in u_p:
        block_rep[user] = []
    predir = os.getcwd()
    file = open(predir+'/'+'block_rep.txt','r')
    lines = file.readlines()
    file.close()
    for line in lines:
        unit=line.strip()
        if unit == "":
            break
        unit = unit.split(":")
        name = unit[0]
        objects = unit[1].split(" ")
        for object in objects:
            if object == "":
                continue
            block_rep[name].append(object)
    return block_rep

def save_block_rep():
    """
    name:object object object
    name:object object object
    """
    predir = os.getcwd()
    file = open(predir+'/'+'block_rep.txt','w')
    for name in block_rep:
        file.write(name + ":")
        for object in block_rep[name]:
            file.write(object + " ")
        file.write("\n")
    file.close()
    return
#----------------------------------------------------------------------

def update(user):  # after a new user has registered, we should use this to update all the global directories
    message_rep[user] = []
    event[user] = threading.Event()
    event[user].clear()
    lasthr_rep[user] = None
    block_rep[user] = []
    return

def de_update(user):  # after a existing user has cancelled himself from the system, we should update all the global directories
    del message_rep[user]
    del event[user]
    del lasthr_rep[user]
    del block_rep[user]
    return

#-------------------- list_block related operation ----------------------
def get_list_block(block):  # the list of blocked users, each of which is a block object, because we need the op and the user-name both
                        # to read the stored information from the outside file
                        # here we don't add the server_stopping time to the accumulated blocking time
    list_block = []
    predir = os.getcwd()
    file = open(predir+'/'+'list_block.txt','r')
    lines = file.readlines()
    file.close()
    for line in lines:
        unit=line.strip()
        if unit == "":
            break
        unit = unit.split(" ")
        object = block(unit[0], float(unit[1]), unit[2])
        list_block.append(object)
    return list_block

def save_list_block():
    """
    self.ip = ip
    self.start = t
    self.name = name
    """
    predir = os.getcwd()
    file = open(predir+'/'+'list_block.txt','w')
    for block in list_block:
        if not block.get_bool():
           continue
        file.write(block.ip + " " + str(block.start) + " " + block.name + "\n")
    file.close()
    return
#----------------------------------------------------------------------

#-------------------- file_rep related operation ----------------------
def get_file_rep(u_p):  # a directory of key-value sender-[(receiver, filename)]; initialize from outside file
    file_rep = {}
    for user in u_p:
        file_rep[user] = []
    predir = os.getcwd()
    file = open(predir+'/'+'file_rep.txt','r')
    lines = file.readlines()
    file.close()
    for line in lines:
        unit=line.strip()
        if unit == "":
            continue
        unit=line.split(" ")
        if (unit[1], unit[2].strip()) not in file_rep[unit[0]]:
            file_rep[unit[0]].append((unit[1], unit[2].strip()))
    return file_rep

def save_file_rep():
    """
    sender receiver filename
    sender receiver filename
    """
    predir = os.getcwd()
    file = open(predir+'/'+'file_rep.txt','w')
    s = ""
    for sender in file_rep:
        for t in file_rep[sender]:
            s = s + sender + " " + t[0] + " " + t[1] + "\n"
    s = s.strip()
    file.write(s)
    file.close()
    return
#----------------------------------------------------------------------

def get_lock(u_p):
    dir = {}
    for user in u_p:
        dir[user] = threading.Lock()
    return dir


PORT = 1452
HOST = socket.gethostbyname(socket.gethostname())
u_p=get_u_p()  # user-pwd directory
#MaxCon = 3  # the biggest # of users permitted to login at the same time
con = 0  # the number of online users AND this variable should be protected!!
lock_con = threading.Lock()
list_block = get_list_block(block)  # the list of blocked users, each of which is a block object, because we need the op and the user-name both
list_user=[]  # a list of user object to demonstrate the online users
#BLOCK_TIME = 60  # block time
CONNECT="""
==================== commands =====================
1.whoelse: display name of other connected users
2.wholasthr: display name of only those users that connected within the last hour
3.broadcast <message>: broadcast <message> to all connected users
4.message <user> <message>: private <message> to a <user>
5.block <user>: blocks the <user> from sending any messages; if <user> is self, display error
6.unblock <user>: unblock the <user> who has been previously blocked; if <user> was not already blocked, display error
7.file <receiver> <filename>: transfer the file <filename> in present working directory to the <receiver>
8.fileget <source> <filename>: get the file from sender <source> temporarily stored in the server; if just "fileget" is applied, then the system will show all the files for you stored in the server
9.filedecline <source> <filename>: delete the remote file <filename> on the server from user <source>
10.logout: log out this user
===================================================
"""
command=["whoelse", "wholasthr", "broadcast", "message", "block", "unblock", "file", "filetransferdec", "filetransfer", "fileget", "filedecline", "logout"]  #existing commands
message_rep=initial_message(u_p, message)  # directory of receiver - message, if there is a message for a receiver, that receiver should be notified by some ways
                # it should contain all the users, for off-line message
file_rep = get_file_rep(u_p)  # a directory of key-value sender-[(receiver, filename)]; initialize from outside file
event=initial_event(u_p)  # a directory to store all the event signals
lasthr_rep=get_lasthr(u_p)  # store all the users' last logging-out time; if one never logged in, it is None
#LAST_HOUR=60  # this is meatured by seconds, so we should multiply 60*60 for an hour
block_rep=get_block(u_p)  # this is a inverted directory, in which the key is the blocked target, and the value is the blocking user
#TIME_OUT = 20  # unactive logging-out time setting
TIME_OUT_CHECK = 5  # this is usually a very small number, to check whether we should log out the main thread of server
list_lastop={}  # record the successfully logging in user's last operation time
(MaxCon, BLOCK_TIME, LAST_HOUR, TIME_OUT) = get_para()  # we can get these parameters from outside file called "para.txt"
SERVER_CHECK = 3  # regularly check whether the main thread of a server's connection should terminate due to user logout or server stop (especially prepared for change of TIME_OUT during the server's running time)
SERVER_STOP = False
log = None  # the file handle of the server log; initialize as None type
lock = get_lock(u_p)  # it's a repository, storing all the message sending locks for each user (now only for message sending)


if __name__ == '__main__':
    pass