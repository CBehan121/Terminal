import os, sys, shlex, subprocess 
from multiprocessing import Process
# here i am simply importing all processes i think necessary 
class MyLilShell():
	# inside my init there is the environ and path to ensure they will stay updated and can be used throughout the program,
	#also there is my dictionary of commands this is used as to send calls to the correct function.
	def __init__(self):

		self.environ = os.environ
		self.path = os.getcwd()
		 
		
		
		self.commands ={ 'cd': self.cd, 
						'dir': self.dir,
						'clr': self.clr,
						'echo' : self.echo,
			 			'pause': self.pause, 
			 			'environ': self.my_environ, 
			 			'quit':self.quit,
			 			'help':self.help
			 			}
	def cd(self, newDir = None ):
		# my cd checks to see if it has gotten an input if it does it will update the path and print the new directory else it will print the path
		# it is also wrapped in a try except incase an incorrect directory is passed
		try:
			if newDir != None:
					os.chdir(newDir)
					self.path = os.getcwd()
					print(os.getcwd())
			else:
				print(self.path)
				
		except:
			print("You dont have this directory")

	def clr(self):
		#My clear function will print the newline character until the screen is cleared like linux
		i = 0 
		while i < 100:
			print("\n")
			i += 1
	def dir(self,newdirectory =  None):
		# My dir function will print the current path and its contense in a neat line by line format.
		try:
			
			directory = os.listdir(newdirectory)
			for item in directory:
					print(item)
			print(self.path)
		except FileNotFoundError:
			print(newdirectory + "not found")
		except NotADirectoryError:
			print(newdirectory + "is not a directory")
			
	def echo(self, words = ""):
		# to ensure that spaces are removed if the words are not wrapped by double quotes i first shlex.split the words 
		output  = shlex.split(words)
		print((" ").join(output)) 
		

	def pause(self, sec = None):
		# my pause is just while loop waiting for you to enter a string of length zero or in other words just press an empty enter.
		print("press enter key to continue")
		while len(input()) != 0:
			input()
		
	def my_environ(self):
		# my environ will print the environ split up with a tab to make t easier to read
		for k,v in self.environ.items():
			print(k + '/t' + v )
	
	def quit(self):
		# my quit throws a SystemExit error 
		sys.exit(0)
	def help(self):
		with open ("readme", "r") as file:
			lines = file.readlines()
			amount = 20
			
			print(*lines[0:20])
			while amount < len(lines):
				
				if len(input()) == 0:
					print(*lines[amount:amount+20])
					amount = amount + 20
def main():
	# first i declare my shell 
	shell = MyLilShell()
	# i create an empty list it is just to be used in case im reading input from a file 
	commandlist = []
	# declare i for iterating through the file lines
	i = 0
	# i have my input sitting in a while true loop to ensure it wont just exit
	while True:
			try:
				# this if loop will go iterate through the given file only if one is given
				if len(commandlist) == 0 and len(sys.argv) > 1:
					filename = sys.argv[1]
					with open (filename, 'r') as file:
						for line in file:
							# here i append each line to my commandlist 
							commandlist.append(line.strip())
					# after ive done everylien i append a quit to close my shell
					commandlist.append("quit")
				#here i am setting my shell path 
				sys.stdout.write("shell=[" + os.getcwd()+ "]--> ")
				# here i check to see if the command list is empty if it is there was no file given so it waits for an input else it runs the commandlist content
				if len(commandlist) == 0:
					unchangedinput = input()
				else:
					unchangedinput = commandlist[i]
				callargs(shell, unchangedinput)
				
				i += 1
				#here are all my unspecific exceptions
				#as the sys.exit error is caught i will throw another to exit the shell
			except SystemExit:
					sys.exit(0)
			except FileNotFoundError:
				print("FileNotFound")
				sys.exit(0)
			except KeyError:
				print("not a command"+ " " + unchangedinput)
				sys.exit(0)
			except TypeError:
				print("incorrect command" +" "+ unchangedinput)
				sys.exit(0)
			
# input is only send here if it has an & on the end, this is my subprocess creator
def ProccessCreate(shell, unchangedinput):
			#shell will be passed between all exterior functions to ensure it stays current
			# i remove the & off the end and send it back to my callargs as a subprocess
			unchangedinput = unchangedinput.split()
			unchangedinput.pop()
			unchangedinput = " ".join(unchangedinput)
			p = Process(target = callargs(shell, unchangedinput))
			p.start()
			
def callargs(shell, unchangedinput):
			# here is where i decided what command needs to go where before it gets executed
			# they are first split into 2 different variables user_cmd the command and edited the argument if there are any
			newInput = unchangedinput.split(" ")
			user_cmd = newInput[0]
			edited = " ".join(newInput[1:])
			#if no input is entered itll simply pass
			
			if user_cmd == "":
				pass
			# if the inout is followed by an & it will be sent to the ProccessCreate function
			elif unchangedinput[-1] == '&':
				ProccessCreate(shell, unchangedinput)
			# if there is a > or >> it will be sent to the outputRedirect function 
			elif " > " in unchangedinput or " >> " in unchangedinput:
				outputRedirect(shell, unchangedinput)
			elif user_cmd not in shell.commands:
			#if i have not made the command that has been entered it will be sent to inbuiltcommands where i fork and run inbuilt linux commands
				inbuiltcommands(unchangedinput)
			# here i decide whether to send the command in with no arguments or with arguments
			elif len(newInput) == 1:
				shell.commands[user_cmd]()
			else:
				shell.commands[user_cmd](edited)
			
def inbuiltcommands(args):
	#here is where the forking begins
	pid = os.fork()
	args = args.split()
	if pid > 0:
		wpid = os.waitpid(pid, 0)
	else:
       
		try:
			os.execvp(args[0], args) 
			
		except Exception as e:

			print("command not found: " + args)
			sys.exit(0)

def outputRedirect(shell, command):
		# here i am redirecting the outputs to files
		command = command.split()
		#i get the filename
		filename = command[-1]
		#args is the rest of the command minus the filename and >> 
		args = " ".join(command[:-2])
		#original is the normal output being stored
		original = sys.stdout
		# i check for >> first just to be safe and set the standard output to the according file appending or writing
		if ">>" in command:
			sys.stdout = open(filename, "a+")
		elif ">" in command:
			sys.stdout = open(filename, "w+")

		# the inout is then sent back to the callargs without the >> > or filename to run as normal but output to the file
		callargs(shell, args)
		# when this has completed the standard output is reset
		sys.stdout = original	
			
		



if __name__ == '__main__':
	 main()