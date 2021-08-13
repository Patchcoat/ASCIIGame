import tkinter as tk
from tkinter import simpledialog
from tkinter import filedialog
from tkinter import messagebox
import os
import json
import math
from enum import Enum

################## Helper Objects ##################
class ConversationType(Enum):
	CHOICE = 1
	TEXT = 2
	NEXT = 3
	END = 4
class DialogBox(object):
	def __init__(self):
		self.id = 0
		self.name = ""
		self.text = []
		self.position = (0,0) # XY position
		self.height = 0
		self.options = []
		self.optionNodes = [] # array of XY positions
		self.type = None
		self.run = ""
		self.area = []
		self.inNode = (0,0) # XY position

class BoxConnection(object):
	def __init__(self):
		self.boxFrom = None
		self.optionFrom = 0
		self.boxTo = None
		self.startPosition = (0,0)
		self.endPosition = (0,0)


################## Application Object ##################
class App(tk.Frame):
	# dialog boxs
	dialogBoxes = []
	boxID = 0
	# connections
	dragConnection = None
	boxConnections = []
	# drag and drop
	dragBox = -1 
	dragNode = -1
	dragStart = (0,0)
	boxStart = (0,0)
	# Right Click Menu
	RCMVisible = False
	RCMPosition = (0,0)
	RCMOptions = []
	# Help Menu
	showHelp = False

	def __init__(self, master):
		super().__init__(master)
		self.master = master
		self.dialogBoxWidth = 200
		self.nodeColor = 'red'
		self.nodeRadius = 5

		if master is not None:
			self.pack()
			self.setup()
			self.bind_inputs()

	def bind_inputs(self):
		self.master.bind("<Button-1>", self.left_click_checker)
		self.master.bind("<ButtonRelease-1>", self.release_checker)
		self.master.bind("<Button-3>", self.right_click_checker)
		self.master.bind("<B1-Motion>", self.drag_handler)
		self.master.bind("<Motion>", self.move_handler)

	def setup(self):
		self.width = 800
		self.height = 500
		self.master.geometry(f"{self.width}x{self.height}")

		self.frame = tk.Frame(self.master)
		self.frame.master.title("Scene")
		self.frame.pack(fill=tk.BOTH, expand=1)

		self.canvas = tk.Canvas(self.frame, bg="white")
		self.canvas.pack(fill=tk.BOTH, expand=1)

		self.draw()
	
	def new_empty_box(self, box):
		box.name = "Name"
		box.text = ["", "", ""]
		box.position = self.RCMPosition
	def new_box_copy(self, box, dialog):
		box.name = dialog.name
		box.text = dialog.text.copy()
		box.type = dialog.type
		box.run = dialog.run
		box.options = dialog.options.copy()
		box.position = (dialog.position[0] + 10, dialog.position[1] + 10)
	def create_new_box(self, dialog=None):
		box = DialogBox()
		box.id = self.boxID
		self.boxID += 1
		if dialog == None:
			self.new_empty_box(box)
		else:
			self.new_box_copy(box, dialog)
		self.dialogBoxes.append(box)
	def created_new_box(self, id):
		self.boxID = id + 1

	def draw_boxes(self):
		for dialog in self.dialogBoxes:
			draw_dialog_box(self.canvas, dialog, self.dialogBoxWidth, self.nodeColor, self.nodeRadius)
	def draw_connections(self):
		if self.dragConnection != None:
			self.canvas.create_line(self.dragConnection.startPosition[0], self.dragConnection.startPosition[1], self.dragConnection.endPosition[0], self.dragConnection.endPosition[1])
		for connection in self.boxConnections:
			self.canvas.create_line(connection.startPosition[0], connection.startPosition[1], connection.endPosition[0], connection.endPosition[1])
	def draw_help(self):
		self.canvas.create_text(8, 8, text="Help", fill="black", font=('Helvetica 12'), anchor="nw")
		if self.showHelp:
			self.canvas.create_rectangle(3, 3, 364, 118, fill="white", outline="black")
			helpText = "Right Click to bring up menu\nEdit attribute by clicking on it\nClick + Drag dialog box to move it\nRight Click dialog box to delete/duplicate the box\nClick + Drag between nodes to make a connection\nRight Click red node to delete a connection\n"
			self.canvas.create_text(6, 6, text=helpText, fill="black", font=('Helvetica 12'), anchor="nw")
	def draw(self):
		self.canvas.delete("all")
		self.draw_boxes()
		self.draw_connections()
		self.draw_help()

	def edit_name(self, dialog):
		answer = simpledialog.askstring("Input", "New Name", parent=self.master)
		if answer is not None:
			dialog.name = answer
			self.draw()
	def ask_text(self):
		# window init
		messageWindow = tk.Toplevel(self.master)
		messageWindow.title("Input")
		# Top Label
		label = tk.Label(messageWindow, text="New Dialog Type")
		label.pack()
		# Text Input
		textBox = tk.Text(messageWindow, height=3, width=30)
		textBox.pack(padx = 3, pady = 10)
		# OK and Cancel Buttons
		result = ""
		def ok_function():
			nonlocal result
			result = textBox.get(1.0,"end")
			messageWindow.destroy()
		def cancel_function():
			nonlocal result
			result = ""
			messageWindow.destroy()
		ok = tk.Button(messageWindow, width=8, text="OK", command=ok_function)
		ok.pack(padx=5, pady=10, side=tk.LEFT)
		cancel = tk.Button(messageWindow, width=8, text="Cancel", command=cancel_function)
		cancel.pack(padx=5, pady=10, side=tk.LEFT)
		# Wait until the window closes
		self.master.wait_window(messageWindow)
		# Return nothing if canceled
		if result == "":
			return None
		result = result.splitlines()
		return result
	def edit_text(self, dialog):
		answer = self.ask_text()
		if answer is not None:
			dialog.text = answer
			self.draw()
	def ask_type(self):
		# window init
		messageWindow = tk.Toplevel(self.master)
		messageWindow.title("Input")
		# Top Label
		label = tk.Label(messageWindow, text="New Dialog Type")
		label.pack()
		# Radio Buttons
		dialogType = tk.IntVar() 
		text = tk.Radiobutton(messageWindow, text="Text", variable=dialogType, value=1)
		choice = tk.Radiobutton(messageWindow, text="Choice", variable=dialogType, value=2)
		next = tk.Radiobutton(messageWindow, text="Next", variable=dialogType, value=3)
		end = tk.Radiobutton(messageWindow, text="End", variable=dialogType, value=4)
		text.pack(anchor="w")
		choice.pack(anchor="w")
		next.pack(anchor="w")
		end.pack(anchor="w")
		# OK and Cancel Buttons
		def cancel_function():
			dialogType.set(0)
			messageWindow.destroy()
		ok = tk.Button(messageWindow, width=8, text="OK", command=lambda: messageWindow.destroy())
		ok.pack(padx=5, pady=10, side=tk.LEFT)
		cancel = tk.Button(messageWindow, width=8, text="Cancel", command=cancel_function)
		cancel.pack(padx=5, pady=10, side=tk.LEFT)
		# Wait until the window closes to return
		self.master.wait_window(messageWindow)
		# Radio Button selection to ConversationType
		if dialogType.get() == 1:
			return ConversationType.TEXT
		elif dialogType.get() == 2:
			return ConversationType.CHOICE
		elif dialogType.get() == 3:
			return ConversationType.NEXT
		elif dialogType.get() == 4:
			return ConversationType.END
		return None
	def edit_type(self, dialog):
		value = self.ask_type()
		if value is not None:
			dialog.type = value
			self.draw()
	def edit_option(self, dialog, option_num):
		answer = simpledialog.askstring("Input", "New Option Text", parent=self.master)
		if answer is not None:
			dialog.options[option_num] = answer
			self.draw()
	def new_option(self, dialog):
		answer = simpledialog.askstring("Input", "New Option Text", parent=self.master)
		if answer is not None:
			dialog.options.append(answer)
			self.draw()
	def read_script(self, path):
		out = ""
		with open(path) as f:
			content = f.readlines()
		for line in content:
			out += line
		if out == "":
			return None
		return out
	def edit_script(self, dialog):
		pythonFiletypes = [('python files', '.py')]
		answer = filedialog.askopenfilename(parent=self.master, initialdir=os.getcwd(), title="Select Script:", filetypes=pythonFiletypes)
		if answer is not None and answer is not '':
			output = self.read_script(answer)
			dialog.run = output

	def sever_connection(self, dialog, inNode=True, option=-1):
		if inNode:
			self.boxConnections = [item for item in self.boxConnections if item.boxTo != dialog]
		else:
			for connection in self.boxConnections:
				if connection.boxFrom == dialog and connection.optionFrom == option:
					self.boxConnections.remove(connection)
					break

	def open_right_click_menu(self, location, options):
		self.RCMPosition = draw_right_click_menu(self.canvas, location, options)
		self.RCMOptions = options
		self.RCMVisible = True

	def right_click_node(self, event):
		self.dragBox = 0
		for dialog in self.dialogBoxes:
			distance = math.sqrt((dialog.inNode[0] - event.x)**2+(dialog.inNode[1] - event.y)**2)
			if distance <= self.nodeRadius:
				self.open_right_click_menu((event.x, event.y), ["Clear Node"])
				self.dragNode = -1
				return True
			self.dragNode = 0
			for node in dialog.optionNodes:
				distance = math.sqrt((node[0] - event.x)**2+(node[1] - event.y)**2)
				if distance <= self.nodeRadius:
					self.open_right_click_menu((event.x, event.y), ["Clear Node"])
					return True
				self.dragNode += 1
			self.dragBox += 1
		return False
	def right_click_box(self, event):
		self.dragBox = len(self.dialogBoxes)-1
		for dialog in reversed(self.dialogBoxes):
			if dialog.position[0] < event.x and dialog.position[0] + 200 > event.x and dialog.position[1] < event.y and dialog.position[1] + dialog.height > event.y:
				self.open_right_click_menu((event.x, event.y), ["Delete Node","Duplicate Node","Cancel"])
				return True
			self.dragBox -= 1
		return False
	def right_click_empty(self, event):
		self.open_right_click_menu((event.x, event.y), ["Add Dialog Box","Load Dialog Graph","Save Dialog Graph"])
	def right_click_checker(self, event):
		self.draw()
		if self.right_click_node(event):
			return
		if self.right_click_box(event):
			return
		self.right_click_empty(event)

	def click_RCM(self, event):
		if not self.RCMVisible:
			return False
		height = len(self.RCMOptions) * 24
		if self.RCMPosition[0] < event.x and self.RCMPosition[0] + 150 > event.x and self.RCMPosition[1] < event.y and self.RCMPosition[1] + height > event.y:
			selection = self.RCMOptions[math.floor((event.y - self.RCMPosition[1])/24)]
			if selection == "Add Dialog Box":
				self.create_new_box()
			elif selection == "Load Dialog Graph":
				read_dialog_graph(self.dialogBoxes, self.boxConnections, self)
			elif selection == "Save Dialog Graph":
				write_dialog_graph(self.dialogBoxes, self.boxConnections)
			elif selection == "Delete Node":
				self.dialogBoxes.pop(self.dragBox)
			elif selection == "Clear Node":
				self.sever_connection(self.dialogBoxes[self.dragBox], self.dragNode == -1, self.dragNode)
			elif selection == "Duplicate Node":
				self.create_new_box(self.dialogBoxes[self.dragBox])
			self.dragBox = -2
			self.draw()
			self.RCMVisible = False
			return True
		return False
	def click_dialog_input_node(self, event, dialog):
		distance = math.sqrt((dialog.inNode[0] - event.x)**2+(dialog.inNode[1] - event.y)**2)
		if distance <= self.nodeRadius:
			self.dragNode = 0
			self.dragConnection = BoxConnection()
			self.dragConnection.boxTo = dialog
			self.dragConnection.startPosition = (event.x, event.y)
			self.dragConnection.endPosition = (dialog.inNode[0], dialog.inNode[1])
			return True
		return False
	def click_dialog_output_node(self, event, dialog):
		nodeNumber = 1
		for node in dialog.optionNodes:
			distance = math.sqrt((node[0] - event.x)**2+(node[1] - event.y)**2)
			if distance <= self.nodeRadius:
				self.sever_connection(dialog, False, nodeNumber-1)
				self.dragNode = nodeNumber
				self.dragConnection = BoxConnection()
				self.dragConnection.boxFrom = dialog
				self.dragConnection.optionFrom = nodeNumber-1
				self.dragConnection.startPosition = (node[0], node[1])
				self.dragConnection.endPosition = (event.x, event.y)
				return True
			nodeNumber += 1
		return False
	def click_dialog_box(self, event, dialog):
		if dialog.position[0] < event.x and dialog.position[0] + 200 > event.x and dialog.position[1] < event.y and dialog.position[1] + dialog.height > event.y:
			self.boxStart = (dialog.position[0], dialog.position[1])
			return True
		return False
	def click_dialog_box_element(self, event):
		self.dragBox = len(self.dialogBoxes)-1
		self.dragStart = (event.x, event.y)
		for dialog in reversed(self.dialogBoxes):
			if self.click_dialog_input_node(event, dialog):
				return True
			if self.click_dialog_output_node(event, dialog):
				return True
			if self.click_dialog_box(event, dialog):
				return False
			self.dragBox -= 1
		self.dragBox = -1
		self.dragNode = -1
		return False
	def edit_dialog_option(self, event):
		hold = self.dragBox
		self.dragBox = -2
		for dialog in reversed(self.dialogBoxes):
			if dialog.position[0] < event.x and dialog.position[0] + 200 > event.x and dialog.position[1] < event.y and dialog.position[1] + dialog.height > event.y:
				height = event.y - dialog.position[1] 
				if height < 24:
					self.dragBox = hold
					return False
				elif height < 46:
					self.edit_name(dialog)
				elif height < 48 + 22 * len(dialog.text):
					self.edit_text(dialog)
				elif height < 72 + 22 * len(dialog.text):
					self.edit_type(dialog)
				elif height < 72 + 22 * len(dialog.text) + 24 * len(dialog.options):
					for option in range(1, len(dialog.options)+1):
						if height < 72 + 22 * len(dialog.text) + 24 * option:
							self.edit_option(dialog, option-1)
							break
				elif height < 96 + 22 * len(dialog.text) + 24 * len(dialog.options):
					self.new_option(dialog)
				elif height < 118 + 22 * len(dialog.text) + 24 * len(dialog.options):
					self.edit_script(dialog)
				return True
		self.dragBox = hold
		return False
	def left_click_checker(self, event):
		if self.click_RCM(event):
			return
		self.RCMVisible = False
		if self.click_dialog_box_element(event):
			return
		if self.edit_dialog_option(event):
			return

	def release_input_node(self, event):
		for dialog in self.dialogBoxes:
			optionInt = 0
			for option in dialog.optionNodes:
				distance = math.sqrt((option[0] - event.x)**2+(option[1] - event.y)**2)
				if distance <= self.nodeRadius:
					self.sever_connection(dialog, False, optionInt)
					self.dragConnection.boxFrom = dialog
					self.dragConnection.optionFrom = optionInt
					self.dragConnection.startPosition = (option[0], option[1])
					self.boxConnections.append(self.dragConnection)
				optionInt += 1
	def release_output_node(self, event):
		for dialog in self.dialogBoxes:
			distance = math.sqrt((dialog.inNode[0] - event.x)**2+(dialog.inNode[1] - event.y)**2)
			if distance <= self.nodeRadius:
				#self.sever_connection(dialog)
				self.dragConnection.boxTo = dialog
				self.dragConnection.endPosition = (dialog.inNode[0], dialog.inNode[1])
				self.boxConnections.append(self.dragConnection)
	def release_cleanup(self):
		self.dragNode = -1
		self.dragBox = -1
		self.dragConnection = None
		self.draw()
	def release_checker(self, event):
		if self.dragNode == 0:
			self.release_input_node(event)
		elif self.dragNode > 0:
			self.release_output_node(event)
		self.release_cleanup()

	def drag_from_node(self, event):
		if self.dragConnection == None:
			return
		if self.dragConnection.boxFrom == None:
			self.dragConnection.startPosition = (event.x, event.y)
		elif self.dragConnection.boxTo == None:
			self.dragConnection.endPosition = (event.x, event.y)
	def drag_move_box(self, displacement):
		self.dialogBoxes[self.dragBox].position = (self.dialogBoxes[self.dragBox].position[0] + displacement[0], self.dialogBoxes[self.dragBox].position[1] + displacement[1])
		for connection in self.boxConnections:
			if connection.boxFrom == self.dialogBoxes[self.dragBox]:
				connection.startPosition = self.dialogBoxes[self.dragBox].optionNodes[connection.optionFrom]
			if connection.boxTo == self.dialogBoxes[self.dragBox]:
				connection.endPosition = self.dialogBoxes[self.dragBox].inNode
	def drag_move_everything(self, displacement):
		for connection in self.boxConnections:
			connection.endPosition = (connection.endPosition[0] + displacement[0], connection.endPosition[1] + displacement[1])
			connection.startPosition = (connection.startPosition[0] + displacement[0], connection.startPosition[1] + displacement[1])
		for box in self.dialogBoxes:
			box.position = (box.position[0] + displacement[0], box.position[1] + displacement[1])
	def drag_handler(self, event):
		displacement = (event.x - self.dragStart[0],event.y - self.dragStart[1])
		self.dragStart = (event.x, event.y)
		if self.dragNode >= 0:
			self.drag_from_node(event)
		elif self.dragBox > -1:
			self.drag_move_box(displacement)
		elif self.dragBox != -2:
			self.drag_move_everything(displacement)
		self.draw()
	
	def move_handler(self, event):
		if event.x < 40 and event.y < 27:
			if not self.showHelp:
				self.showHelp = True
				self.draw()
			self.showHelp = True
		elif self.showHelp:
			self.showHelp = False
			self.draw()


################## Write to Json ##################
def create_dialog_boxes(dialogBoxes):
	boxes = {}
	for box in dialogBoxes:
		boxObj = {}
		boxObj['id'] = box.id
		boxObj['name'] = box.name
		boxObj['text'] = box.text
		boxObj['position'] = box.position
		boxObj['options'] = []
		for option in box.options:
			boxObj['options'].append((option, -1))
		boxObj['type'] = {ConversationType.CHOICE:"CHOICE",
						   ConversationType.TEXT:"TEXT",
						   ConversationType.NEXT:"NEXT",
						   ConversationType.END:"END"}.get(box.type, "NONE")
		boxObj['run'] = box.run
		boxes[box.id] = boxObj
	return boxes
def create_dialog_connections(boxes, boxConnections, dialogBoxes):
	for connection in boxConnections:
		count = 0
		for box in dialogBoxes:
			if connection.boxFrom == box:
				if connection.boxTo == None:
					boxes[count]['options'][connection.optionFrom] = (boxes[count]['options'][connection.optionFrom][0], -1)
				else:
					boxes[count]['options'][connection.optionFrom] = (boxes[count]['options'][connection.optionFrom][0], connection.boxTo.id)
			count += 1
	return boxes
def write_dialog_file(boxes, filePath):
	jsonOutput = json.dumps(boxes)
	print(jsonOutput)
	if filePath is not None:
		with open(filePath, 'w') as file:
			file.truncate(0)
			file.write(jsonOutput)
			file.close()
def write_dialog_graph(dialogBoxes, boxConnections):
	boxes = create_dialog_boxes(dialogBoxes)
	boxes = create_dialog_connections(boxes, boxConnections, dialogBoxes)
	filePath = filedialog.asksaveasfile(filetypes=[('Dialog File', '.dlg')])
	write_dialog_file(boxes, filePath)

################## Read from Json ##################
def read_dialog_file(file):
	if file is None or file == '':
		return None
	out = ""
	with open(file) as f:
		content = f.readlines()
	for line in content:
		out += line
	if out == "":
		return None
	return json.loads(out)
def load_dialog_boxes(boxes, dialogBoxes, app):
	dialogBoxes.clear()
	highest = 0
	dialogBoxIndex = {}
	for boxKey in boxes:
		box = boxes[boxKey]
		dialogBox = DialogBox()
		dialogBox.id = box["id"]
		if dialogBox.id > highest:
			highest = dialogBox.id
		dialogBox.name = box["name"]
		dialogBox.text = box["text"]
		dialogBox.position = box["position"]
		dialogBox.type = {"NONE":None,
						  "CHOICE":ConversationType.CHOICE, 
						  "TEXT":ConversationType.TEXT, 
						  "NEXT":ConversationType.NEXT, 
						  "END":ConversationType.END}.get(box["type"], None)
		dialogBox.run = box["run"]
		for option in box["options"]:
			dialogBox.options.append(option[0])
		dialogBoxes.append(dialogBox)
		dialogBoxIndex[dialogBox.id] = dialogBox
	return (dialogBoxIndex, highest)
def load_dialog_connections(boxes, boxConnections, dialogBoxIndex):
	boxConnections.clear()
	for boxKey in boxes:
		if len(boxes[boxKey]["options"]) > 0:
			box = boxes[boxKey]
			for item in range(len(box["options"])):
				if box["options"][item][1] > -1:
					connection = BoxConnection()
					connection.boxFrom = dialogBoxIndex[box["id"]]
					connection.optionFrom = item
					connection.boxTo = dialogBoxIndex[box["options"][item][1]]
					connection.startPosition = dialogBoxIndex[box["id"]].optionNodes[item]
					connection.endPosition = dialogBoxIndex[box["options"][item][1]].inNode
					boxConnections.append(connection)
def read_dialog_graph(dialogBoxes, boxConnections, app):
	if len(dialogBoxes) > 0 or len(boxConnections) > 0:
		answer = messagebox.askyesno(title="Save",message="Save Dialog Graph?")
		if answer:
			write_dialog_graph(dialogBoxes, boxConnections)
	filePath = filedialog.askopenfilename(filetypes=[('Dialog File', '.dlg')])
	boxes = read_dialog_file(filePath)
	if boxes == None:
		return
	load_return = load_dialog_boxes(boxes, dialogBoxes, app)
	app.created_new_box(load_return[1])
	app.draw()
	load_dialog_connections(boxes, boxConnections, load_return[0])


################## Draw Dialog Box ##################
def draw_bounding_box(canvas, left, top, right, bottom):
	canvas.create_rectangle(left, top, right, bottom, outline="black", width=1, fill="white")
	top = top+24
	canvas.create_line(left, top, right, top)
	return top

def draw_title(canvas, left, top, right, dialogBox, color, nodeRadius):
	canvas.create_text(left+6,top+3, text=dialogBox.name, fill="black", font=('Helvetica 12'), anchor="nw")
	canvas.create_line(left, top+22, right, top+22)
	midpoint = top + 11
	canvas.create_oval(left-nodeRadius, midpoint+nodeRadius, left+nodeRadius, midpoint-nodeRadius, fill=color)
	dialogBox.inNode = (left, midpoint)

def draw_text(canvas, left, top, right, dialogBox):
	top = top + 2
	lineNum = 0
	for line in dialogBox.text:
		lineNum += 1
		top = top + 22
		canvas.create_text(left+3,top, text=line, fill="black", font=('Helvetica 12'), anchor="nw")
		if lineNum != len(dialogBox.text):
			canvas.create_line(left, top+20, right, top+20, fill="grey")
	top = top+20
	canvas.create_line(left, top, right, top)
	return top

def type_to_string(type):
	if type == None:
		return "NONE"
	elif type == ConversationType.CHOICE:
		return "CHOICE"
	elif type == ConversationType.NEXT:
		return "NEXT"
	elif type == ConversationType.TEXT:
		return "TEXT"
	elif type == ConversationType.END:
		return "END"
def draw_type(canvas, left, top, right, type):
	canvas.create_text(left+3, top+3, text="Type: " + type_to_string(type), fill="black", font=('Helvetica 12'), anchor="nw")
	top = top+24
	canvas.create_line(left, top, right, top)
	return top

def draw_dialog_options(canvas, left, top, right, dialogBox, color, nodeRadius):
	dialogBox.optionNodes = []
	for option in dialogBox.options:
		canvas.create_text(left+3, top+5, text=option, fill="black", font=('Helvetica 12'), anchor="nw")
		midpoint = top + 12
		canvas.create_oval(right-nodeRadius, midpoint+nodeRadius, right+nodeRadius, midpoint-nodeRadius, fill=color)
		dialogBox.optionNodes.append((right, midpoint))
		top = top + 24
		canvas.create_line(left, top, right, top)
	return top

def draw_new_option_button(canvas, left, top, right):
	canvas.create_text((left+right)/2, top+5, text="NEW OPTION", fill="black", font=('Helvetica 12'), anchor="n")
	top = top+24
	canvas.create_line(left, top, right, top)
	return top

def draw_script_button(canvas, left, top, right):
	canvas.create_text((left+right)/2, top+5, text="SCRIPT", fill="black", font=('Helvetica 12'), anchor="n")

def calculate_bottom(top, text_len, options_len):
	return top + 22 * text_len + 24 * options_len + 118

def draw_dialog_box(canvas, dialogBox, width, color, nodeRadius):
	# setup
	left = dialogBox.position[0]
	top = dialogBox.position[1]
	right = left + width
	bottom = calculate_bottom(top, len(dialogBox.text), len(dialogBox.options))
	dialogBox.height = bottom - top
	
	# draw the box
	top = draw_bounding_box(canvas, left, top, right, bottom)
	draw_title(canvas, left, top, right, dialogBox, color, nodeRadius)
	top = draw_text(canvas, left, top, right, dialogBox)
	top = draw_type(canvas, left, top, right, dialogBox.type)
	top = draw_dialog_options(canvas, left, top, right, dialogBox, color, nodeRadius)
	top = draw_new_option_button(canvas, left, top, right)
	draw_script_button(canvas, left, top, right)


################## Draw Right Click Menu ##################
def draw_rcm_bounding_box(canvas, left, top, right, bottom):
	canvas.create_rectangle(left, top, right, bottom, outline="black", width=1, fill="white")

def draw_option(canvas, left, top, right, option_text, end):
	canvas.create_text(left+3, top+5, text=option_text, fill="black", font=('Helvetica 12'), anchor="nw")
	if not end:
		top = top+24
		canvas.create_line(left, top, right, top)
	return top

def draw_right_click_menu(canvas, position, options):
	width = 150
	# setup
	left = position[0]
	top = position[1]
	right = left + width
	bottom = top+len(options)*24

	draw_rcm_bounding_box(canvas, left, top, right, bottom)
	for option in options:
		top = draw_option(canvas, left, top, right, option, option==options[-1])

	return position


################## Main Function ##################
def main():
	# TODO fix saving error
	root = tk.Tk()
	app = App(master=root)
	app.mainloop()

if __name__=="__main__":
	main()