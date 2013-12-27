import urwid
import re
import pygame                   # required to play sounds
import os
import os.path

logging = False
if logging:
    logfile = open("log.txt", "a")
def log(entry):
    if logging:
        logfile.write(entry + "\n")
        logfile.flush()

# class borrowed from        
# http://crossplatform.net/sublime-text-ctrl-p-fuzzy-matching-in-python/
class FuzzyMatcher():
    def __init__(self):
        self.pattern = ''
    def setPattern(self, pattern):
        self.pattern = '.*?'.join(map(re.escape, list(pattern)))
    def score(self, string):
        match = re.search(self.pattern, string, re.I)
        if match is None:
            return 0
        else:
            return 100.0 / ((1 + match.start()) * (match.end() - match.start() + 1))


class SText(urwid.Text):
    _selectable = True
    def keypress(self, size, key):
        return key #Let parent widget deal with processing keys

fuzzy = FuzzyMatcher()
#use a small buffer size to decrease latency
pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
directory = '/home/josh/sounds'
searchstring = ''

list_of_files = os.listdir(directory)
sounds = {}
sounds= {}
widgets = []
for file in list_of_files:
    if os.path.isfile(directory + "/" + file):
        try:
            sounds[file] = pygame.mixer.Sound(directory + "/" + file)
        except:
            pygame.error

for name in sounds:
    widgets.append(urwid.AttrMap(SText(name, wrap='clip'), 'inversegreen', focus_map='boldgreen'))

sflw = urwid.SimpleFocusListWalker(widgets)
lb = urwid.ListBox(sflw)

def handleinput(key):
    global searchstring
    if len(key) == 1:
        searchstring += key
    elif key == 'esc':
        searchstring = ''
    elif key in ['backspace', 'delete']:
        searchstring = searchstring[:-1]
    elif key == 'enter':
        if searchstring == ":q":
            raise urwid.ExitMainLoop()
        searchstring = ''
        if lb.focus:
            play_sound(lb.focus.base_widget.get_text()[0])
    fuzzy.setPattern(searchstring)
    updateheader()
    updatelist()

def play_sound(name):
    sounds[name].play()

def updatelist():
    global sflw
    for i in range(len(sflw)):
        sflw.pop()
    for i in sorted(widgets, key=lambda x: -fuzzy.score(x.base_widget.text)):
        if fuzzy.score(i.base_widget.text):
            sflw.append(i)
        
header = urwid.Text('')

def updateheader():
    header.set_text(searchstring)

updatelist()
frame = urwid.Frame(lb, header)
palette = [('boldgreen', 'black,bold', 'dark green'),
           ('inversegreen', 'dark green,bold', 'black'),]
loop = urwid.MainLoop(frame, palette, unhandled_input=handleinput, screen=urwid.raw_display.Screen(), handle_mouse=False)
loop.run()
