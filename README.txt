Simple Server-Client Chatting Program
sy2515, Shuo Yang

a. A brief description of your code:
This is a multi-threads based chatting program, consisting both the server part and the client part. The server program will run first followed by multiple instances of the client program (each instance supports one client). There are new user registration (old user de-registration, or cancellation in other words), user login and authentication (including blocking after several consecutive login failures, new login user notification, logout user notification), user commands (including “whoelse”, “wholasthr”, “broadcast”, “message”, “block”, “unblock”, file transferring related and “logout”), login user TIME_OUT check, maximum supported users online, server log generation, server commands (including system parameters check and modification, user related information check, and manually stopping server), server database backup when it stops, and so on. All these features and how to use them will be talked about in details in the following several parts.

The client program has two working threads when after the user has logged in. At the very beginning, it receives the parameters from the python execution command line input (the server’s IP and port number), and creates a new socket, and uses it to connect the remote server. At this time, if the server has reached its online users limitation, this new connection will be dropped right now and the person now can’t login. If the server has not reached its online users limitation, then this user enters the name-password check status, which is also in previous main thread, and in which the person can use existing user-name with password to login, or this person can register new user (de-register old user). After the authentication, this person just logs in with his user-name and password, and then two separate working threads are generated, in which one is responsible for taking the input from the command line and send it to the server, and another is responsible for listening for the server on this connection and deal with different situations based on the pre-defined protocols. The previous main thread is just waiting there for the client program termination signal, which is passed from the listening thread. By this design model, we can quit the client program when we want, and we can achieve the communication for this login user with the server.

The server also has two separate threads for each login user. From the very beginning, the server program receives the parameters (just the allocated port number) from the python execution command line input, and creates the socket and bind the present IP and port with it. After this, two more threads will separately generated, one for server administrator commands operations, and another for listening for the new client socket connection. The previous main thread of the server is just waiting there for the signal to quit, which always comes from the server administrator commands operation thread, or comes from the KeyboardInterupt generated just in this thread. This means the server can be stopped both by administrator command, and by “Ctrl+C”. In the listening for new client socket connection thread, the socket can generate one new thread when there is someone want to login, in which the authentication function will applied first. Of course, this thread can also support new user registration and old user de-registration. During the name-pad check process, the user existing or not and user being blocked or not and user online or not will be checked, and corresponding response will be given. In this session, there are three times for a user to wrongly type his password, after which that user will be blocked on that IP for a given BLOCK_TIME. (If a user is blocked, people cannot login on that machine using that user name, but people can login on that machine using other user names, and people can login on other machines using that user name, all during the BLOCK_TIME period.) Of course, the blocking principle also works during someone de-registers his existing user, and that failure counts for the total failure times, but only in this connection session, which means that if that person just quit this client program and open a new one on that machine, he can still have three times to try. In registration and de-registration parts, the user name sensitivity and existing or not and being blocked or not and online or not will be carefully checked, and if you wrongly type something, you will be given another change to have a try. All of these designs are error prevention oriented and human-friendly oriented. After the previous login thread, the user can formally log in to the server, and perform several pre-defined commands on the server. Just at this time, two separate threads will be generated, one for sending messages to the client, and another for listening for the messages from the client, and the previous login thread is just waiting there to check TIME_OUT issues or for the quit signal from his sub-threads (actually from the listening thread). The listening thread will receive whatever message from the client, and perform the corresponding operations. And the sending thread will send the message from the server, the broadcasting, and the private message to this client. I have carefully checked all the running status of these threads, and make sure that they are running out when they should be. Because leftover threads which should be killed at some time in the past will eat some resources of the system, and also bring some bugs for the whole system’s function. Making sure to quit each threads really takes me some time. I keep all the variables and resources which should be shared among all the threads as global variables, and when the server stops, I backup all the system parameters and database into outside files, which will be discussed later on.


b. Details on development environment:
system: Mac OS X 10.9.1
language: Python 2.7.3
IDE: PyCharm


c. Instructions on how to run your codes:
There are no Makefile needed. Just run the Server.py script on the host and the Client.py on user’s machine, as instructed below:
for server: Python Serevr.py 1234 (in which 1234 is the port number allocated to the server)
for client: Python Client.py 12.12.12.12 1234 (in which 12.12.12.12 is server’s IP, and 1234 is port number allocated to that server)

After that, server program is just running and listening for connections, and you can also perform the administration operations directly on the same console. (actually in real word this administrator thread should be put in another console, or UI, and this is easy to happen, because it is right a separate thread from others) And the client program is running under the ckeck-in part, in which you should enter your user-name and password, or you can register (de-register) in this part. After you successfully log in to the server, you can perform several commands. I have made the instructions in the running program as clear as possible, and you can just follow them.


d. Sample commands to invoke your code:
server:
####################################################################
sy2515@warsaw:~/PA1$ python Server.py 1231
Server is running now...
Server is listening for connections now...

online users
[admin]The present online users are:
facebook on 128.59.15.36:45657
Columbia on 160.39.222.87:55824

blocked users
[admin]The present blocked users are:
Google on 160.39.222.87 at 2014-03-04_21:25:13

all users
[admin]The present all users are:
"Google" with password "hasglasses"
"Columbia" with password "116bway"
"network" with password "seemsez"
"SEAS" with password "winterbreakisover"
"foobar" with password "passpass"
"wikipedia" with password "donation"
"windows" with password "withglass"
"facebook" with password "wastingtime"
"csee4119" with password "lotsofexams"

MaxCon
[admin]The present permittable maximum user connection # is:
5

BLOCK_TIME 
[admin]The present BLOCK_TIME is:
60.0 seconds

LAST_HOUR
[admin]The present LAST_HOUR is:
100.0 seconds

TIME_OUT
[admin]The present TIME_OUT is:
600.0 seconds

change MaxCon
[admin]Please enter your new MaxCon parameter: (in int format)
4
The MaxCon has been changed to 4

change BLOCK_TIME
[admin]Please enter your new BLOCK_TIME parameter: (in float format and it will represent how many seconds)
50
The BLOCK_TIME has been changed to 50.0

change LAST_HOUR
[admin]Please enter your new LAST_HOUR parameter: (in float format and it will represent how many seconds)
120
The LAST_HOUR has been changed to 120.0

change TIME_OUT
[admin]Please enter your new TIME_OUT parameter: (in float format and it will represent how many seconds)
500
The TIME_OUT has been changed to 500.0
####################################################################
special notes:
1. MaxCon: the allowed maximum number of online users, for workload issue of the server; this is the number of the actual login users, but not the opening client programs, which means that if MaxCon is 5, you can still open 10 client programs but none of them has successfully logged in to the server; but if the online users number is already 5, you cannot try to open a client program, and you will be declined; but if you have already opened a client program, and the online users number has just reached 5, then you can still try to enter your name/pwd, but once your information is verified, you will then be notified that “the limitation has been reached and you will logout automatically”; I know this may be some kind of curious; this results from that a person on the client program can actually not have successfully logged in to the server;
2. BLOCK_TIME: the blocking time after 3 login failures, in seconds for convenience of testing;
3. LAST_HOUR: the time before what in the past we want to see who were online, in seconds for convenience of testing;
4. TIME_OUT: inactive time to automatically logout from the server, in seconds for convenience of testing;
5. you can change all the above system parameters both in server administrator console, and in the outside file called “para.txt”, like:
MaxCon 5
BLOCK_TIME 60.0
LAST_HOUR 100.0
TIME_OUT 600.0
you should keep the MaxCon as Int, and the left three as Float when you enter them both in console and directly in the setting file; the last three parameters represent the time in seconds; these are all for testing convenience;

client:
####################################################################
sy2515@warsaw:~/PA1$ python Client.py 128.59.15.36 1231
Now you are trying to connect to the Chatting room! You should log in first. Type required information and hit enter!
Please enter your username: (or you can "quit" or "resigter" or "de-resigter" by those commands)
>>
facebook
Please enter your password:
>>
wastingtime
Welcome to the Chatting room user "facebook"! Now you have successfully logged in!
facebook>>
System(broadcast): "Columbia" has just logged in.
facebook>>
System(broadcast): "Google" has just logged in.
facebook>>
wholes
The other users are:
Columbia
Google

facebook>>
wholasthr
The wholasthr users are:
Columbia
Google

facebook>>
broadcast It's me facebook ~
facebook(broadcast): It's me facebook ~

facebook>>
message Columbia I want to try private message~

facebook>>
message csee4119 I want to try off-line message~
The user "csee4119" is unfortunately not online. But the server has stored your message.

facebook>>
block facebook
Error! You cannot block yourself! Please try again!..

facebook>>
block Columbia
You have successfully blocked Columbia from sending you messages.

facebook>>
unblock Columbia
You have successfully unblocked Columbia

facebook>>
logout 
You have logged out! See you again!


sy2515@warsaw:~/PA1$ python Client.py 128.59.15.36 1231
Now you are trying to connect to the Chatting room! You should log in first. Type required information and hit enter!
Please enter your username: (or you can "quit" or "resigter" or "de-resigter" by those commands)
>>
Columbia
The present user is being logged in. Please use another user to log-in:
>>


sy2515@warsaw:~/PA1$ python Client.py 128.59.15.36 1231
Now you are trying to connect to the Chatting room! You should log in first. Type required information and hit enter!
Please enter your username: (or you can "quit" or "resigter" or "de-resigter" by those commands)
>>
facebook
Please enter your password:
>>
12
Wrong password! You have 2 times to give another try for this user on this machine in this connection session!
Please enter your username:
>>
facebook
Please enter your password:
>>
12
Wrong password! You have 1 times to give another try for this user on this machine in this connection session!
Please enter your username:
>>
facebook
Please enter your password:
>>
12
Wrong password for 3 times. You are blocked. Please try to log-in with this user after 50.0 seconds. Or you can try another user in this machine.
>>
facebook
You are blocked! Please wait, you have 39.7975831032 time left to log in using this name again!
You can try another user:
>>


shuoyang@dyn-160-39-222-87:~/CN/PA1 $ python Client.py 128.59.15.36 1231
Now you are trying to connect to the Chatting room! You should log in first. Type required information and hit enter!
Please enter your username: (or you can "quit" or "resigter" or "de-resigter" by those commands)
>>
csee4119
Please enter your password:
>>
lotsofexams
Welcome to the Chatting room user "csee4119"! Now you have successfully logged in!
csee4119>>
The off-line messages during you are not in:
facebook(broadcast): It's me facebook ~
facebook(private): I want to try off-line message~
Now you can input commands as above instructed:
csee4119>>
Time out for 60.0 seconds.
shuoyang@dyn-160-39-222-87:~/CN/PA1 $ 

####################################################################
special notes:
1. off-line chat function is also for broadcast command;
2. we can’t send message to oneself, error message will be given;
3. we can’t block oneself; not to say block himself; error message will be given;
4. we can’t block a blocked user, and unblock an unblocked user; error message will be given;
5. about the blocking after 3 login failures, as mentioned before: if a user is blocked, people cannot login on that machine using that user name, but people can login on that machine using other user names, and people can login on other machines using that user name, all during the BLOCK_TIME period; this means that when you try to login but are blocked, you are still in the client program and you can still run the client program on that machine and try other user names;
6. “wholasthr” will not show the user himself;
7. a user can also receive the “broadcast” message from himself;
8. you can’t login an already online user;


e. Description of an additional functionalities and how they should be executed/tested:
1. server log:
After the server stops, all the running status and user login/logout/commands records will be saved as a log, named by the stopping time of the server like:
log_2014-03-04_21:32:30.log

You can check the system information during the running time of the server through this log.

2. all the system parameters and user information will be saved if the server is stopping:
####################################################################
……
The server_stop notification has been sent to all the online clients, and they will automatically log out right now.
[backup]MaxCon, BLOCK_TIME, LAST_HOUR, TIME_OUT all have been stored.
[backup]user_password repository has been stored.
[backup]message_rep has been stored.
[backup]file_rep has been stored.
[backup]block_rep has been stored.
[backup]list_block has been stored.
The server is being stopped via administrator operation.
The server has stoped! Bye!
[backup]server log has been saved.
sy2515@warsaw:~/PA1$ 
####################################################################
and they are saved as:
para.txt: system parameters described as before
user_pass.txt: all the users with their passwords
message_rep.txt: all the messages (from system and other users during message, broadcast and file-transfer
) for all users which have not been sent due to some reasons such as off-line reasons
file_rep.txt: all the file-transfer information which have not been processed
block_rep.txt: all the user blocking information generated by user command “block”
list_block.txt: all the blocked users and their IP and blocking time information

They all have their formats and the server program can read them from start, and save them at the end.

3. new user registration and old user de-registration:
just type “register” or “de-register” after you just enter the client program:
####################################################################
sy2515@warsaw:~/PA1$ python Client.py 128.59.15.36 1231
Now you are trying to connect to the Chatting room! You should log in first. Type required information and hit enter!
Please enter your username: (or you can "quit" or "resigter" or "de-resigter" by those commands)
>>
register
Please enter your new user name:
>>
shuo
Please enter your new password:
>>
123
Please re-enter your password:
>>
123
You have successfully registered "shuo". Please continue!
Please enter your username: (or you can "quit" or "resigter" or "de-resigter" by those commands)
>>
shuo
Please enter your password:
>>
123
Welcome to the Chatting room user "shuo"! Now you have successfully logged in!
shuo>>
quit
You are leaving the chatting room! See you again!
sy2515@warsaw:~/PA1$ python Client.py 128.59.15.36 1231
Now you are trying to connect to the Chatting room! You should log in first. Type required information and hit enter!
Please enter your username: (or you can "quit" or "resigter" or "de-resigter" by those commands)
>>
de-register
Please enter your existing user name:
>>
shuo
Please enter your password:
>>
123
Password verified. Are you sure to cancel your registration for shuo? Enter "yes" or "no":
>>
yes
You have successfully cancelled "shuo". Please continue!
Please enter your username: (or you can "quit" or "resigter" or "de-register" by those commands)
>>
####################################################################

4. New login user notification and logout user notification:
When a user has just logged in, a notification will be sent to all the online users (this message is not off-line, because it’s not useful). Also, if a user has just logged out from the server, an notification will also be sent to all the present online users. You will see this during you running the program. I will not show it here.

5. server stop:
There are two ways: “stop” command in the server console, or “Ctrl+C”. In both situations the online users will be notified and log out automatically.

6. data concurrency:
I have carefully considered the data concurrency program, and tentatively have a try at two places.
a. The number of the total present online users. This is a global variable in server’s running environment. I just give a lock and release it before and after operation on this variable.
b. File transfer VS normal message sending. As I don’t created another separate thread for file transferring, when do this kind of job, I should stop normal message sending to the targeting user. Otherwise the normal message will be also written to the received file. I set a lock for each user, I will give and release the lock before and after these operations. Then problem is solved.

7. file transfer:
I have stored a “test_file.txt” in the folder for testing convenience.
####################################################################
sy2515@warsaw:~/PA1$ python Client.py 128.59.15.36 1231
Now you are trying to connect to the Chatting room! You should log in first. Type required information and hit enter!
Please enter your username: (or you can "quit" or "resigter" or "de-resigter" by those commands)
>>
facebook
Please enter your password:
>>
wastingtime
Welcome to the Chatting room user "facebook"! Now you have successfully logged in!
facebook>>
System(broadcast): "Columbia" has just logged in.
facebook>>
file Columbia test_file.txt
Now begin transfering, please wait...
Transferring process succeeds.
file "test_file.txt" has been successfully received by the server.
facebook>>


shuoyang@dyn-160-39-222-87:~/CN/PA1 $ python Client.py 128.59.15.36 1231
Now you are trying to connect to the Chatting room! You should log in first. Type required information and hit enter!
Please enter your username: (or you can "quit" or "resigter" or "de-resigter" by those commands)
>>
Columbia
Please enter your password:
>>
116bway
Welcome to the Chatting room user "Columbia"! Now you have successfully logged in!
Columbia>>
facebook(file_transfer): test_file.txt
Columbia>>
fileget
File "test_file.txt" from "facebook".
Columbia>>
fileget facebook test_file.txt
server ready, now client receive file
Please wait until the "receive file success" notification has raised!...
receive file success!
Columbia>>
####################################################################
special notes:
1. file transfer has its notification for the receiver; file transfer notification can be also saved off-line and given when that user log in;
2. file not existing and other possible errors have been carefully checked;
3. commands:
->file <receiver> <filename>: transfer the file <filename> in present working directory to the <receiver>
->fileget <source> <filename>: get the file from sender <source> temporarily stored in the server; if just "fileget" is applied, then the system will show all the files for you stored in the server
->filedecline <source> <filename>: delete the remote file <filename> on the server from user <source>

8. all kinds of brute quits:
for the client:
	before login:
		“Ctrl+C” can be used and the server will receive this information and take corresponding reaction
		closing the terminal window can be used and the server will receive this information and take corresponding reaction
	after login:
		“Ctrl+C” is not supported, because the Keyboard input function is in another thread and KeyboardInterupt cannot be captured
		closing the terminal window can be used and the server will receive this information and take corresponding reaction
for the server:
	before the user has logged in:
		“Ctrl+C” can be used but the client program will also in running status; at this time, two random input and notification of no response from server will be given, and you can quit the client program; actually I think this situation is not that frequent, because the server is not always stopping, and also the possibility that the user is in login session when the server stops is very small
		closing the terminal window can be used, but the problem is also as above discussed
	after the user has logged in:
		“Ctrl+C” can be used and the client will receive this information and quit gracefully
		closing the terminal window will not be used by now, and the online user will run crazy; it’s kind of trivial and as it is not mentioned in the discussion board, I did not solve it; but there is definitely a way to deal with it if time is enough
