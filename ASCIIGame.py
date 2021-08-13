import curses
import random
import time
import threading
from enum import Enum
from math import sin
from math import sqrt

# player class
class Player(object):
    def __init__(self):
        self.pos = [25, 14]
        self.oldPos = self.pos
        self.screen = [1,5]

# conversation classes
class ConversationType(Enum):
    CHOICE = 1
    TEXT = 2
    NEXT = 3
    END = 4
class ConversationNode(object):
    def __init__(self):
        self.name = ""
        self.text = []
        self.options = []
        self.type = None
        self.run = None
    def node_run(self):
        if self.run == None:
            return
        self.run()

class ConversationOption(object):
    def __init__(self):
        self.text = ""
        self.next = None

class Conversation(object):
    def __init__(self):
        self.subject = None
        self.tree = ConversationNode()
        self.response = ""
        self.savedResponse = ""

# character class
class Character(object):
    def __init__(self):
        self.conversation = None
        self.position = []
        self.screen = []

# item class
class Item():
    def __init__(self):
        self.position = []
        self.screen = []
        self.hit = False
        self.on_hit = None
        self.on_leave = None
        self.icon = ""

# screen animation class
class Anim():
    def __init__(self):
        self.start = 0 # start time
        self.step = 0
        self.times = [] # time spent in each stage, seconds
        self.anims = [] # animation functions

# game class
class Game(object):
    def __init__(self):
        self.pause = False

        self.displayTextBox = False
        self.textBoxText = []
        self.displayConversation = False
        self.uiSelection = 0
        self.uiMaxSelection = 0

        self.movedScreens = False
        self.animatedScreen = False
        self.screenSize = [50,30]
        self.currentScreen = [[' ']*self.screenSize[1] for i in range(self.screenSize[0])]
        self.frame = []
        self.screen = None

        self.player = Player()

        self.characters = []
        self.generate_characters()
        self.conversation = Conversation()

        self.items = []
        self.generate_items()

        self.anim = Anim()
        self.generate_animation()

    ############### Generation Functions ###############
    def generate_characters(self):
        bridgekeeper = Character()
        bridgekeeper.position = [30, 15]
        bridgekeeper.screen = [10,5]

        def bridgekeeper_new_conversation():
            convo = ConversationNode()
            convo.name = "Bridgekeeper"
            convo.text = ["","You may pass",""]
            convo.type = ConversationType.END
            convo.options = []
            return convo

        def color_yes_run():
            newPosition = self.conversation.subject.position
            if self.player.pos[1] < self.conversation.subject.position[1]:
                newPosition[1] += 1
            else:
                newPosition[1] -= 1
            self.conversation.subject.position = newPosition
            self.conversation.subject.conversation = bridgekeeper_new_conversation()
            self.movedScreens = True

        def player_kill():
            self.pause = True

        def bridgekeeper_conversation():
            bridgekeeperConvo = ConversationNode()
            bridgekeeperConvo.name = "Bridgekeeper"
            bridgekeeperConvo.text = ["","You wish to cross my bridge?",""]
            bridgekeeperConvo.type = ConversationType.CHOICE
            bridgekeeperConvo.options = []
            #last outcome
            colorYes = ConversationNode()
            colorYes.name = "Bridgekeeper"
            colorYes.text = ["","    You may pass.    ", ""]
            colorYes.type = ConversationType.END
            colorYes.run = color_yes_run
            colorNo = ConversationNode()
            colorNo.name = "Narator"
            colorNo.text = ["","You are flung into the air and fall into the", "chasm.", "",
                            "Game Over", ""]
            colorNo.type = ConversationType.NEXT
            colorNo.run = player_kill
            #fourth question
            fourthQuestion = ConversationNode()
            fourthQuestion.name = "Bridgekeeper"
            fourthQuestion.text = ["","Your favorite color is $RESPONSE?", ""]
            fourthQuestion.type = ConversationType.CHOICE
            fourthQuestion.options = [ConversationOption(), ConversationOption()]
            fourthQuestion.options[0].text = "No"
            fourthQuestion.options[0].next = colorNo
            fourthQuestion.options[1].text = "Yes"
            fourthQuestion.options[1].next = colorYes
            #third question
            thirdQuestion = ConversationNode()
            thirdQuestion.name = "Bridgekeeper"
            thirdQuestion.text = ["","What... is your favorite color?", ""]
            thirdQuestion.type = ConversationType.TEXT
            thirdQuestion.options = [ConversationOption()]
            thirdQuestion.options[0].text = ""
            thirdQuestion.options[0].next = fourthQuestion
            #second question
            secondQuestion = ConversationNode()
            secondQuestion.name = "Bridgekeeper"
            secondQuestion.text = ["","What... is your quest?", ""]
            secondQuestion.type = ConversationType.TEXT
            secondQuestion.options = [ConversationOption()]
            secondQuestion.options[0].text = ""
            secondQuestion.options[0].next = thirdQuestion
            #first question
            firstQuestion = ConversationNode()
            firstQuestion.name = "Bridgekeeper"
            firstQuestion.text = ["","What... is your name?", ""]
            firstQuestion.type = ConversationType.TEXT
            firstQuestion.options = [ConversationOption()]
            firstQuestion.options[0].text = ""
            firstQuestion.options[0].next = secondQuestion
            #secon option
            bkCNo = ConversationNode()
            bkCNo.name = "Bridgekeeper"
            bkCNo.text = ["","Then be gone with you!",""]
            bkCNo.type = ConversationType.END
            bkCYes = ConversationNode()
            bkCYes.name = "Bridgekeeper"
            bkCYes.text = ["","Then you must answer my questions three.",""]
            bkCYes.type = ConversationType.CHOICE
            bkCYes.options = [ConversationOption()]
            bkCYes.options[0].text = "Alright"
            bkCYes.options[0].next = firstQuestion
            #first option
            yesOption = ConversationOption()
            noOption = ConversationOption()
            yesOption.text = "Yes"
            yesOption.next = bkCYes
            noOption.text = "No"
            noOption.next = bkCNo
            bridgekeeperConvo.options.append(noOption)
            bridgekeeperConvo.options.append(yesOption)

            return bridgekeeperConvo

        bridgekeeper.conversation = bridgekeeper_conversation()

        beachlover = Character()
        beachlover.position = [22, 17]
        beachlover.screen = [0,5]
        def beachlover_conversaion():
            convo = ConversationNode()
            convo.name = "Beach Lover"
            convo.text = ["","I love the beach!","Don't you?"]
            convo.type = ConversationType.CHOICE
            convo.options = []

            yes = ConversationNode()
            yes.name = "Beach Lover"
            yes.text = ["","Yeah!"]
            yes.type = ConversationType.END
            yes.options = []
            no = ConversationNode()
            no.name = "Beach Lover"
            no.text = ["", "Oh...","Nevermind."]
            no.type = ConversationType.END

            convoYes = ConversationOption()
            convoYes.text = "Yes"
            convoYes.next = yes
            convoNo = ConversationOption()
            convoNo.text = "No"
            convoNo.next = no

            convo.options.append(convoNo)
            convo.options.append(convoYes)

            return convo
        beachlover.conversation = beachlover_conversaion()

        wiseguide = Character()
        wiseguide.position = [20, 13]
        wiseguide.screen = [2,5]
        def wiseguide_conversation():
            convo = ConversationNode()
            convo.name = "Bearded Man"
            convo.text = ["Good day to you, fine traveler!","How may I help you?"]
            convo.type = ConversationType.CHOICE
            convo.options = []

            nods = ConversationNode()
            nods.name = "Bearded Man"
            nods.text = ["","Come back anytime."]
            nods.type = ConversationType.END

            thankYou = ConversationOption()
            thankYou.text = "Thank you, that is all"
            thankYou.next = nods

            howHelp = ConversationNode()
            howHelp.name = "Bearded Man"
            howHelp.text = ["","How may I help you?"]
            howHelp.type = ConversationType.CHOICE

            needHelp = ConversationOption()
            needHelp.text = "I have another question"
            needHelp.next = howHelp

            help1 = ConversationNode()
            help1.name = "Bearded Man"
            help1.text = ["Ah. There is a portal to the north.",
                          "Step through and it will take you just west of",
                          "your ultimate destination"]
            help1.type = ConversationType.CHOICE
            help1.options = [thankYou, needHelp]

            help2 = ConversationNode()
            help2.name = "Bearded Man"
            help2.text = ["","This is the Zylinder Forest","To the west is a beach",
                          "To the east are the cliffs"]
            help2.type = ConversationType.CHOICE
            help2.options = [thankYou, needHelp]

            help3 = ConversationNode()
            help3.name = "Bearded Man"
            help3.text = ["","I know of a man west of here who sits on the","beach"]
            help3.type = ConversationType.CHOICE
            help3.options = [thankYou, needHelp]

            convoHelp1 = ConversationOption()
            convoHelp1.text = "I am the professor/TA grading this and want to get it done as soon as possible"
            convoHelp1.next = help1
            convoHelp2 = ConversationOption()
            convoHelp2.text = "What is this place?"
            convoHelp2.next = help2
            convoHelp3 = ConversationOption()
            convoHelp3.text = "Is there anyone else here?"
            convoHelp3.next = help3

            howHelp.options = [convoHelp1, convoHelp2, convoHelp3]

            convo.options.append(convoHelp1)
            convo.options.append(convoHelp2)
            convo.options.append(convoHelp3)

            return convo
        wiseguide.conversation = wiseguide_conversation()

        self.characters = [bridgekeeper, beachlover, wiseguide]

    def generate_items(self):
        stone = Item()
        stone.screen = [1,5]
        stone.position = [20,11]
        stone.icon = '?'
        def stone_on_hit():
            self.displayTextBox = True
            if self.displayTextBox and self.player.screen == [1,5]:
                self.textBoxText = ["Carved Stone in the Ground","",
                            "Welcome to Color Quest",
                            "     Go East and cross the bridge     ", ""]
        stone.on_hit = stone_on_hit
        def stone_on_leave():
            self.displayTextBox = False
        stone.on_leave = stone_on_leave

        portal = Item()
        portal.screen = [2,4]
        portal.position = [25,15]
        portal.icon = 'O'
        def portal_on_hit():
            #self.change_screen([9,5])
            self.anim.start = time.time()
            self.change_screen([-1,-1])
        portal.on_hit = portal_on_hit

        self.items.append(stone)
        self.items.append(portal)

    def generate_animation(self):
        self.anim.times = [0, 1, 1, 0]
        def prep_function(_runtime):
            self.pause = True
            random.seed(13)
            return self.generate_wilderness()

        def circle(center, radius, background):
            screen = background

            preCalc = -(center[1]**2) + radius**2

            for i in range(0, self.screenSize[0]):
                for j in range(0, self.screenSize[1]):
                    if sqrt((i-25)**2 + (j-15)**2) <= radius:
                        screen[i][j] = ' '
            
            for i in range(0, self.screenSize[0]):
                innerRoot = preCalc + 2*center[1]*i - i**2
                if innerRoot <= 0:
                    continue
                otherHalf = sqrt(innerRoot)
                pos1 = int(center[0] - otherHalf)
                pos2 = int(center[0] + otherHalf)
                if pos1 > 0 and pos1 < self.screenSize[0] and i > 0 and i < self.screenSize[1]:
                    screen[pos1][i] = '.'
                if pos2 > 0 and pos2 < self.screenSize[0] and i > 0 and i < self.screenSize[1]:
                    screen[pos2][i] = '.'

            return screen

        def circle_grow(runtime):
            random.seed(13)
            screen = circle([25,15], runtime*30, self.generate_wilderness())
            return screen

        def circle_shrink(runtime):
            if runtime != 0:
                random.seed(29)
                screen = circle([25,15], 30-runtime*30, self.generate_wilderness())
            return screen

        def teleport(_runtime):
            self.player.screen = [9,5]
            self.pause = False
            random.seed(29)
            return self.generate_wilderness()

        self.anim.anims = [prep_function, circle_grow, circle_shrink, teleport]

    ############### Drawing ###############
    # Environment Drawing
    def place_character(self, screen):
        for character in self.characters:
            if self.player.screen == character.screen:
                screen[character.position[0]][character.position[1]] = 'H'

    def place_item(self, screen):
        for item in self.items:
            if self.player.screen == item.screen:
                screen[item.position[0]][item.position[1]] = item.icon

    def generate_wilderness(self):
        screen = [[' '] * self.screenSize[1] for i in range(self.screenSize[0])]
        for i in range(1, self.screenSize[0] - 1):
            for j in range(1, self.screenSize[1] - 1):
                if random.randint(0, 30) == 0:
                    screen[i][j] = 'T' # place a tree
        self.place_item(screen)
        self.place_character(screen)
        return screen

    def cliff_line(self, screen):
        position = 30
        bridgeStart = 0
        prevDir = 0

        for j in range(0, self.screenSize[1]):
            char = ''
            chars = ['/','|','\\']
            direction = random.randint(-1,1)
            if j > self.screenSize[1] - 7:
                if position > 30:
                    direction = -1
                elif position < 30:
                    direction = 1
                elif position == 30:
                    direction = 0
            if self.player.screen[1] == 5 and (j >= 14 and j <= 16):
                bridgeStart = position
                direction = 0
            else:
                position += direction
                if position > 35:
                    position = 35
                    direction = 0
                elif position < 25:
                    position = 25
                    direction = 0
            char = chars[direction + 1]
            if prevDir != 0 and prevDir != direction:
                position -= direction

            if j == 0:
                position = 30
            screen[position][j] = char
            prevDir = direction

        return bridgeStart

    def generate_eastern_cliffs(self):
        screen = [[' '] * self.screenSize[1] for i in range(self.screenSize[0])]
        for i in range(1, 10):
            for j in range(1, self.screenSize[1] - 2):
                if random.randint(0, 30) == 0:
                    screen[i][j] = 'T'
        
        bridgeStart = self.cliff_line(screen)
        
        # bridge
        if self.player.screen[1] == 5:
            for i in range(bridgeStart, self.screenSize[0]):
                screen[i][15] = '#'

        self.place_item(screen)
        self.place_character(screen)
        return screen

    def water_wave(self, position, anim_time):
        height = (sin(anim_time)+1)
        offset = sin(anim_time) * 1.5 + 15
        horiz = sin(position) * height + offset
        return int(horiz)

    def generate_western_sea(self):
        screen = [[' '] * self.screenSize[1] for i in range(self.screenSize[0])]
        for i in range(40,self.screenSize[0] - 1):
            for j in range(1, self.screenSize[1] - 1):
                if random.randint(0, 30) == 0:
                    screen[i][j] = 'T'

        for j in range(0, self.screenSize[1]):
            position = self.water_wave(j, time.time())
            screen[position][j] = '.'

        self.place_item(screen)
        self.place_character(screen)
        return screen

    def generate_portal(self):
        screen = self.currentScreen

        runtime = time.time() - self.anim.start
        screen = self.anim.anims[self.anim.step](runtime)
        if runtime > self.anim.times[self.anim.step]:
            self.anim.step += 1
            self.anim.start = time.time()

        return screen

    def generate_screen(self):
        # *2 means the x coordinate is always an even number
        # *2+1 means the y coordinate is always an odd number
        # this prevents the terrain from being flipped over the diagonal
        random.seed(self.player.screen[0] * 2 + self.player.screen[1] * 2 + 1)
        self.animatedScreen = False
        if self.player.screen[0] == 10:
            return self.generate_eastern_cliffs()
        if self.player.screen[0] == 0:
            self.animatedScreen = True
            return self.generate_western_sea()
        if self.player.screen[0] == -1:
            self.animatedScreen = True
            return self.generate_portal()

        return self.generate_wilderness()

    def draw_frame(self):
        frame1 = curses.newpad(2,self.screenSize[0]+3)
        frame2 = curses.newpad(2,self.screenSize[0]+3)
        frame3 = curses.newpad(self.screenSize[1]+2,2)
        frame4 = curses.newpad(self.screenSize[1]+2,2)
        self.frame = [frame1, frame2, frame3, frame4]
        for x in range(0, self.screenSize[0]+1):
            self.frame[0].addch(0, x, ord('-'))
            self.frame[1].addch(0, x, ord('-'))
        self.frame[0].addch(0,0, ord('+'))
        self.frame[0].addch(0,self.screenSize[0]+1, ord('+'))
        self.frame[0].addstr(0,int(self.screenSize[0] / 2) - 5,"Color Quest", curses.A_BOLD)
        self.frame[1].addch(0,0, ord('+'))
        self.frame[1].addch(0,self.screenSize[0]+1, ord('+'))
        for y in range(0, self.screenSize[1]):
            self.frame[2].addch(y,0, ord('|'))
            self.frame[3].addch(y,0, ord('|'))

    def draw_screen(self):
        self.screen = curses.newpad(self.screenSize[1]+1,self.screenSize[0]+1)
        for y in range(0, self.screenSize[1]):
            for x in range(0, self.screenSize[0]):
                self.screen.addch(y,x, ord(self.currentScreen[x][y]))

    # UI Drawing
    def draw_text_box(self):
        if len(self.textBoxText) == 0:
            return
        maxNum = 0
        for line in self.textBoxText:
            if maxNum < len(line):
                maxNum = len(line)
        width = maxNum+2
        if width > self.screenSize[0]:
            box = curses.newpad(2,2)
            box.addch(0,0,ord('+'))
            box.addch(1,1,ord('+'))
            return
        height = len(self.textBoxText) + 1
        box = curses.newpad(height+1, width+1)

        for i in range(height):
            box.addch(i,0,'|')
            box.addch(i,width-1,'|')

        titleCenter = int((maxNum - len(self.textBoxText[0])) / 2)
        if 2 + titleCenter * 2 + len(self.textBoxText[0]) != width:
            box.addstr(0,0,'+' + '-'*titleCenter + self.textBoxText[0] + '-'*titleCenter + '-+')
        else:
            box.addstr(0,0,'+' + '-'*titleCenter + self.textBoxText[0] + '-'*titleCenter + '+')
        box.addstr(height-1,0,'+' + ('-' * maxNum) + '+')

        for i in range(1,len(self.textBoxText)):
            out = self.textBoxText[i]
            if len(out) < maxNum:
                out = " " * int((maxNum-len(out)) / 2 + 1) + out
            box.addstr(i,1,out)

        position_x = int((self.screenSize[0] - width) / 2)
        position_y = int((self.screenSize[1] - height) / 2)
        box.noutrefresh(0,0,position_y,position_x,height+position_y-1,width+position_x-1)

    def draw_conversation(self):
        height = 10
        convoBox = curses.newpad(height, self.screenSize[0])

        convoBox.addstr(0,0, "-"*self.screenSize[0])
        name = self.conversation.tree.name
        convoBox.addstr(0,int((self.screenSize[0] - len(name)) / 2), name)

        for i in range(len(self.conversation.tree.text)):
            text = self.conversation.tree.text[i]
            text = text.replace('$RESPONSE', self.conversation.savedResponse)
            convoBox.addstr(i+1,1, text)

        if self.conversation.tree.type == ConversationType.CHOICE:
            self.uiMaxSelection = -1
            for i in range(len(self.conversation.tree.options)):
                convoBox.addstr(height-2-(i*2), 3, self.conversation.tree.options[i].text)
                self.uiMaxSelection += 1
            convoBox.addch(height - 2 - (self.uiSelection*2),1,ord('>'))
        elif self.conversation.tree.type == ConversationType.TEXT:
            convoBox.addstr(height-3, 3, self.conversation.response)
            convoBox.addch(height-3, len(self.conversation.response) + 3, ord('|'))

        position_y = self.screenSize[1] - height + 1
        convoBox.noutrefresh(0,0 ,position_y,1, position_y+height-1, self.screenSize[0]+1)

    # The draw function
    def draw(self):
        if self.movedScreens or self.animatedScreen:
            self.currentScreen = self.generate_screen()
            self.draw_screen()
            self.movedScreens = False
        self.screen.addch(self.player.oldPos[1], self.player.oldPos[0],
                        ord(self.currentScreen[self.player.oldPos[0]][self.player.oldPos[1]]))
        self.screen.addch(self.player.pos[1], self.player.pos[0], ord('@'))
        self.player.oldPos = self.player.pos.copy()

        if self.displayConversation:
            self.screen.noutrefresh(0,0, 1,1, self.screenSize[1]-10,self.screenSize[0])
        else:
            self.screen.noutrefresh(0,0, 1,1, self.screenSize[1],self.screenSize[0])

        if self.displayTextBox:
            self.draw_text_box()

        if self.displayConversation:
            self.draw_conversation()

        self.frame[0].noutrefresh(0,0, 0,0, 0,curses.COLS-1)
        self.frame[1].noutrefresh(0,0, self.screenSize[1]+1,0, self.screenSize[1]+1,self.screenSize[0]+2)
        self.frame[2].noutrefresh(0,0, 1,0, self.screenSize[1],0)
        self.frame[3].noutrefresh(0,0, 1,self.screenSize[0]+1, self.screenSize[1],self.screenSize[0]+2)
        curses.doupdate()

    ############### Game Logic ###############
    def check_next(self, newPos, char):
        return self.currentScreen[newPos[0]][newPos[1]] == char

    def check_items(self):
        for item in self.items:
            if self.player.screen == item.screen:
                if self.player.pos == item.position:
                    item.on_hit()
                    item.hit = True
                if self.player.pos != item.position and item.hit:
                    item.on_leave()
                    item.hit = False

    def change_screen(self, screen):
        self.player.screen = screen
        self.currentScreen = self.generate_screen()
        self.movedScreens = True

    def border_crossing(self, newPos, i):
        screen = self.player.screen
        if newPos[i] < 0:
            # keeps the player from moving too far left
            if i == 0 and screen[i] == 0:
                return
            # move up or left a screen
            screen[i] -= 1
            if screen[i] < 0:
                screen[i] = 10
            self.change_screen(screen)
            self.player.pos[i] = self.screenSize[i] - 1
        elif newPos[i] >= self.screenSize[i]:
            # display the win text when the player reaches the end
            if i == 0 and screen[i] == 10:
                self.pause = True
                self.displayTextBox = True
                self.textBoxText = ["","",
                        "You won!",
                        "    Thanks for playing!    ",""]
                return
            # move down or right a screen
            screen[i] += 1
            if screen[i] > 10:
                screen[i] = 0
            self.change_screen(screen)
            self.player.pos[i] = 0

    def check_for_character(self, newPos):
        if self.check_next(newPos, 'H'):
            for char in self.characters:
                if self.player.screen == char.screen and newPos == char.position:
                    self.displayConversation = True
                    self.conversation.tree = char.conversation
                    self.conversation.subject = char

    def player_move(self, x, y):
        newPos = self.player.pos.copy()
        newPos[0] += x
        newPos[1] += y

        for i in range(2):
            border = newPos[i] < 0 or newPos[i] >= self.screenSize[i]
            wall = False
            if not (newPos[0] >= self.screenSize[0] or newPos[1] >= self.screenSize[1]):
                wall = self.check_next(newPos, 'T')
                wall = wall or self.check_next(newPos, '|')
                wall = wall or self.check_next(newPos, '\\')
                wall = wall or self.check_next(newPos, '/')
                wall = wall or self.check_next(newPos, '_')
                wall = wall or self.check_next(newPos, 'H')
            bridge = self.currentScreen[self.player.pos[0]][self.player.pos[1]] == '#'
            if not border and not wall and (not bridge or i == 0):
                self.player.pos[i] = newPos[i]
            elif border:
                self.border_crossing(newPos, i)
            elif wall:
                self.check_for_character(newPos)

        self.check_items()

    ############### Input ###############
    def ui_move(self, direction):
        newSelection = self.uiSelection
        newSelection -= direction
        if newSelection < 0:
            newSelection = self.uiMaxSelection
        elif newSelection > self.uiMaxSelection:
            newSelection = 0
        elif direction == 0:
            if self.conversation.tree.type == ConversationType.CHOICE:
                self.conversation.tree = self.conversation.tree.options[self.uiSelection].next
                self.uiSelection = 0
            elif self.conversation.tree.type == ConversationType.TEXT:
                self.conversation.tree = self.conversation.tree.options[0].next
                self.conversation.savedResponse = self.conversation.response
                self.conversation.response = ""
                self.conversation.tree.node_run()
            elif self.conversation.tree.type == ConversationType.NEXT:
                self.conversation.tree.node_run()
            elif self.conversation.tree.type == ConversationType.END:
                self.displayConversation = False
                self.conversation.tree.node_run()
            return
        self.uiSelection = newSelection

    def ui_type(self, key):
        if self.conversation.tree.type != ConversationType.TEXT:
            return
        if key == 8 or key == curses.KEY_BACKSPACE:
            self.conversation.response = self.conversation.response[:-1]
            return
        self.conversation.response += chr(key)

    # The input function
    def inputs(self, stdscr):
        c = stdscr.getch()
        if c == 27:
            return True
        if self.pause:
            return False
        if self.displayConversation:
            if c == 450 or c == curses.KEY_UP:
                self.ui_move(-1)
            elif c == 456 or c == curses.KEY_DOWN:
                self.ui_move(1)
            elif c == 10 or c == curses.KEY_ENTER:
                self.ui_move(0)
            elif c >= 65 or c <= 122:
                self.ui_type(c)
            elif c == 8 or c == curses.KEY_BACKSPACE:
                self.ui_type(c)
            return False
        if c == 450 or c == curses.KEY_UP:
            self.player_move(0,-1)
        if c == 456 or c == curses.KEY_DOWN:
            self.player_move(0,1)
        if c == 454 or c == curses.KEY_RIGHT:
            self.player_move(1,0)
        if c == 452 or c == curses.KEY_LEFT:
            self.player_move(-1,0)
        return False

    ############## Loop ##############
    # The Loop (please no flash photography)
    def loop(self, stdscr):
        drawThread = DrawThread(1, "Draw-Thread", self)
        inputThread = InputThread(2, "Input-Thread", stdscr, self)
        drawThread.start()
        inputThread.start()
        while not exit:
            pass
        drawThread.join()
        inputThread.join()

# threads
EXIT = False
class DrawThread(threading.Thread):
    def __init__(self, threadID, name, game):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.game = game
    def run(self):
        global EXIT
        curses.curs_set(0)
        while True:
            self.game.draw()
            if EXIT:
                break

class InputThread(threading.Thread):
    def __init__(self, threadID, name, stdscr, game):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.stdscr = stdscr
        self.game = game
    def run(self):
        global EXIT
        while True:
            EXIT = self.game.inputs(self.stdscr)
            if EXIT:
                break

# functions that init and de-init curses
def start(game):
    stdscr = curses.initscr()
    curses.noecho()
    curses.cbreak()
    stdscr.keypad(True)
    win = curses.newwin(curses.LINES - 1, curses.COLS - 1, 0, 0)
    curses.curs_set(0)
    game.currentScreen = game.generate_screen()
    game.draw_frame()
    game.draw_screen()

    return stdscr

def end(stdscr):
    curses.nocbreak()
    stdscr.keypad(False)
    curses.echo()
    curses.endwin()


# main function (as if you couldn't tell)
def configure():
    print("+"+"-"*50+"+")
    for i in range(2):
        print("|"+" "*50+"|")
    print("| Resize the terminal so it is at least big enough |")
    print("|     to fit this frame (it can be bigger) then    |")
    print("|                   press 'enter'.                 |")
    print("|                                                  |")
    print("|                 arrow keys to move               |")
    print("|                    esc to exit                   |")
    print("| ? = item                                         |")
    print("| T = tree                                         |")
    print("| H = human                                        |")
    for i in range(19):
        print("|"+" "*50+"|")
    print("+"+"-"*50+"+")
    x = input()

def main():
    configure()
    game = Game()
    stdscr = start(game)
    game.loop(stdscr)
    end(stdscr)

if __name__ == "__main__":
    main()
