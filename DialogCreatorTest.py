from DialogCreator import \
	create_dialog_boxes, create_dialog_connections, read_dialog_file, write_dialog_file,\
	load_dialog_boxes, load_dialog_connections, \
	App, ConversationType, DialogBox, BoxConnection
import json
import pytest

boxes_out = {1: {"name":"Box1", "id":1}, 2: {"name":"Box2", "id":2}}
boxes_in =  {"1": {"id":1, "name":"Box1", "text":["","",""], "position":(0,0), "type":"CHOICE", "run":"", 
					"options":[]}, 
			 "2": {"id":2, "name":"Box2", "text":["","Text",""], "position":(1,1), "type":"END", "run":"Run",
			 		"options":[["Yes",1]]}}

# Dialog Read
def test_read_dialog_file(tmpdir):
	global boxes_out
	file = tmpdir.join('output.dlg')
	file.write(json.dumps(boxes_out))
	output = read_dialog_file(file.strpath)
	for item in output:
		output[int(item)] = output.pop(item)
	assert output == boxes_out

def test_load_dialog_boxes():
	global boxes_in
	dialogBoxes = []
	app = App(None)
	loadReturn = load_dialog_boxes(boxes_in, dialogBoxes, app)
	assert dialogBoxes[0].id == 1
	assert dialogBoxes[0].name == "Box1"
	assert dialogBoxes[0].text == ["","",""]
	assert dialogBoxes[0].position == (0,0)
	assert dialogBoxes[0].type == ConversationType.CHOICE
	assert dialogBoxes[0].run == ""
	assert dialogBoxes[0].options == []
	assert dialogBoxes[1].id == 2
	assert dialogBoxes[1].name == "Box2"
	assert dialogBoxes[1].text == ["","Text",""]
	assert dialogBoxes[1].position == (1,1)
	assert dialogBoxes[1].type == ConversationType.END
	assert dialogBoxes[1].run == "Run"
	assert dialogBoxes[1].options == ["Yes"]
	assert loadReturn[1] == 2

def test_load_dialog_connections():
	global boxes_in
	boxConnections = []
	Box1 = DialogBox()
	Box1.id = 1
	Box1.inNode = 2
	Box2 = DialogBox()
	Box2.id = 2
	Box2.optionNodes = [1]
	dialogBoxIndex = {1:Box1, 2:Box2}
	load_dialog_connections(boxes_in, boxConnections, dialogBoxIndex)
	assert boxConnections[0].boxFrom == Box2
	assert boxConnections[0].optionFrom == 0
	assert boxConnections[0].boxTo == Box1

# Dialog Write
def test_write_dialog_file(tmpdir):
	global boxes_in
	file = tmpdir.join('output.dlg')
	write_dialog_file(boxes_in, file.strpath)
	assert file.read() == json.dumps(boxes_in)

def test_create_dialog_boxes():
	boxes_in = []
	box1 = DialogBox()
	box1.id = 0
	box1.name = "fred"
	box1.text = ["","",""]
	box1.position = (1,1)
	box1.options = ["option 1", "option 2"]
	box1.type = ConversationType.CHOICE
	box1.run = "Hello World"
	box2 = DialogBox()
	box2.id = 1
	box2.name = "fred"
	box2.text = ["","oops",""]
	box2.position = (2,2)
	box2.options = ["option 2", "option 2"]
	box2.type = ConversationType.CHOICE
	box2.run = "Hello World"
	boxes_in.append(box1)
	boxes_in.append(box2)
	boxes = create_dialog_boxes(boxes_in)
	count = 0
	for box in boxes:
		assert boxes[box]['id'] == boxes_in[count].id
		assert boxes[box]['name'] == boxes_in[count].name
		assert boxes[box]['text'] == boxes_in[count].text
		assert boxes[box]['position'] == boxes_in[count].position
		count2 = 0
		for option in boxes_in[count].options:
			assert boxes[box]['options'][count2][0] == option
			count2 += 1
		assert boxes[box]['type'] == "CHOICE"
		assert boxes[box]['run'] == boxes_in[count].run
		count += 1

def test_create_dialog_connections():
	dialogBoxes = []
	box1 = DialogBox()
	box1.id = 0
	box1.name = "fred"
	box1.text = ["","",""]
	box1.position = (1,1)
	box1.options = ["option 1", "option 2"]
	box1.type = ConversationType.CHOICE
	box1.run = "Hello World"
	box2 = DialogBox()
	box2.id = 1
	box2.name = "fred"
	box2.text = ["","oops",""]
	box2.position = (2,2)
	box2.options = ["option 2", "option 2"]
	box2.type = ConversationType.CHOICE
	box2.run = "Hello World"
	dialogBoxes.append(box1)
	dialogBoxes.append(box2)
	boxesDict = {0: {'options':[("first",-1), ("second",-1)]}, 1: {'options':[("hello",-1),("goodbye",-1)]}}
	connections = []
	connection = BoxConnection()
	connection.boxFrom = box1
	connection.optionFrom = 0
	connection.boxTo = box2
	connections.append(connection)
	boxes = create_dialog_connections(boxesDict, connections, dialogBoxes)
	assert boxes[0]['options'][0][1] == 1

# Editing
def test_edit_script():
	pass

# Box Creation
def test_new_empty_box():
	app = App(None)
	box = DialogBox()
	app.new_empty_box(box)
	assert box.name == "Name"
	assert box.text == ["", "", ""]
	assert box.type == None

def test_new_box_copy():
	app = App(None)
	box = DialogBox()
	dialog = DialogBox()
	dialog.name = "Test"
	dialog.run = "Run"
	dialog.text = ["", "test", ""]
	dialog.type = ConversationType.END
	dialog.options = ["Option1", "Option2", "Option3"]
	app.new_box_copy(box, dialog)
	assert box.name == "Test"
	assert box.run == "Run"
	assert box.text == ["", "test", ""]
	assert box.type == ConversationType.END
	assert box.options == ["Option1", "Option2", "Option3"]

def test_create_new_box():
	app = App(None)
	app.create_new_box(None)
	box = app.dialogBoxes[0]
	assert box.name == "Name"
	assert box.id == 0
	assert box.text == ["", "", ""]
	assert box.type == None
	dialog = DialogBox()
	dialog.name = "Test"
	dialog.id = 0
	dialog.run = "Run"
	dialog.text = ["", "test", ""]
	dialog.type = ConversationType.END
	dialog.options = ["Option1", "Option2", "Option3"]
	app.create_new_box(dialog)
	box = app.dialogBoxes[1]
	assert box.name == "Test"
	assert box.id == 1
	assert box.run == "Run"
	assert box.text == ["", "test", ""]
	assert box.type == ConversationType.END
	assert box.options == ["Option1", "Option2", "Option3"]

def test_created_new_box():
	app = App(None)
	app.created_new_box(10)
	assert app.boxID == 11

# Box and Connection Editing
def test_read_script(tmpdir):
	app = App(None)
	file = tmpdir.join("test.py")
	with open(file.strpath, 'w') as f:
		f.write("Test Function")
	assert app.read_script(file.strpath) == "Test Function"

def test_sever_connection():
	app = App(None)
	app.create_new_box(None)
	app.dialogBoxes[0].options.append("Option")
	app.create_new_box(None)
	connection = BoxConnection()
	connection.boxFrom = app.dialogBoxes[0]
	connection.optionFrom = 0
	connection.boxTo = app.dialogBoxes[1]
	app.boxConnections.append(connection)
	app.sever_connection(app.dialogBoxes[1])
	assert len(app.boxConnections) == 0

# Call the main function that is part of pytest so that
# the test functions in this file will start executing.
pytest.main(["-v", "--tb=line", "-rN", "DialogCreatorTest.py"])