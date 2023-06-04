import PySimpleGUI as sg
import tkinter as tk
from tkinter import filedialog
import os

import requests

from abc import abstractmethod
import subprocess
import language_tool_python

SERVER_ADDRESS = "127.0.0.1"

class User:
    def __init__(self, username : str = "", password : str = "") -> None:
        self.username : str = username
        self.password : str = password

    def update_details(self, username : str = "", password : str = "") -> bool: # TODO add validation
        self.username : str = username
        self.password : str = password

class Fs_worker:
    def __init__(self, cloud_credentials = None) -> None:
        self.cloud_credentials = cloud_credentials

    def save(content : str, file_path : str):
        try:
            f = open(file_path, "w")
            f.write(content)
        except:
            print("Error saving file!")

    def cloud_save(content : str):
        pass

class Editor:
    def search(text : str, substring : str) -> int:
        return text.find(substring)

class Updater:
    def check_for_update() -> bool:
        return True
    
    def download_update() -> None:
        # TODO
        pass

    def run_updater() -> None:
        subprocess.Popen('update.exe')

class Doc_checker:
    @abstractmethod
    def check(self, text) -> list:
        pass

    @abstractmethod
    def fix(self, text) -> str:
        pass

class Grammar_checker(Doc_checker):
    def __init__(self) -> None:
        super().__init__()
        self.tool= language_tool_python('en-US')

    def check(self, text) -> list:
        mistakes = self.tool.check(text)
        for mistake in mistakes:
            print(mistake)
        return mistakes

    def fix(self, text) -> str:
        return self.tool.correct(text)

class Spell_checker(Doc_checker):
    def check(self, text) -> list:
        pass

    def fix(self, text) -> str:
        pass

class Compiler:
    @abstractmethod
    def check(self, text):
        pass

    @abstractmethod
    def compile(self, text):
        pass

    @abstractmethod
    def run(self, text):
        pass

def CPP_compiler(Compiler):
    def check(self, text):
        pass

    def compile(self, text):
        pass

    def run(self, text):
        pass

def Java_compiler(Compiler):

    def compile(self, text) -> bool:
        java_compiler_output = os.system("javac *.java")
        if java_compiler_output == 0:
            return True
        else:
            return False

    def run(self, text, filename):
        if compile(text=text):
            run_string = "java " + filename
            java_output = os.system(run_string)
        if java_output == 0:
            return True
        else:
            return False

class Collaboration_worker:
    def __init__(self) -> None:
        self.users : list = []
        self.user : User

    def add_user(self, user : str):
        # TODO this should send something to the server
        if self.users.__contains__(user) == False:
            self.users.append(user)

    def update_user(self, user):
        self.user = user

    def sync(self):
        payload = {"user": self.user.username}
        response = requests.get(SERVER_ADDRESS + '/collaborate/')
    

class GUI:
    current_user = User()

    menu_def = [
        ['File', ['Open', 'Save', 'Save As']], 
        ['Compiler', ['Compile Java', 'Run Java']], 
        ['Terminal', ['Open in SciTE', 'Open in system shell']], 
        ['Collaborate', ['Login', 'Invite user', 'End session']], 
        ['Checker', ['Language check', 'Fix language']]]
    # All the stuff inside your window. This is the sg magic code compactor...
    layout =    [[sg.Menu(menu_def)],
                [sg.Multiline("", key='textarea',
                expand_x=True, expand_y=True)]]

    # Create the Window
    window = sg.Window('SciTe mockup', layout, size=(1280, 720), resizable=True)
    # Event Loop to process "events"
    while True:             
        event, values = window.read()
        collab_worker = Collaboration_worker()
        filepath = None

        if event:
            print(event)
        if event == 'Login':
            username = sg.popup_get_text("Please enter your username:")
            password = sg.popup_get_text("Please enter your password:")
            current_user.update_details(username=username, password=password)

        if event == 'Open':
            try:
                filepath = filedialog.askopenfilename()
                f = open(filepath, "r")
                # TODO populate text area with contents
                window['textarea'].update(f.read())
                f.close()
            except:
                sg.popup_error("Whoops!")
            

        if event == 'Save':
            if filepath != None:
                content = window['textarea']
                fsworker = Fs_worker()
                fsworker.save(content, filepath)
            else:
                sg.popup_error("No filepath set!")

        if event == 'Save As':
            try:
                filepath = filedialog.askopenfilename()
                content = window['textarea']
                fsworker = Fs_worker()
                fsworker.save(content, filepath)
            except:
                sg.popup_error("Whoops!")

        if event == 'Invite user':
            username = sg.popup_get_text("Who do you want to invite?")
            collab_worker.add_user(username)
            
        if event == 'Language check':
            pass

        if event == 'Open in SciTe':
            second_layout = [[sg.Multiline('Term-Output')],
                             [sg.Multiline('Term-Input'), sg.Button('Run')]]
            second_window = sg.Window("Terminal", second_layout)
            while True:
                event2, values2 = second_window.read()

                if event2 == 'Run':
                    output = subprocess.check_output(second_window['Term-Input']).decode('utf-8')
                    second_window['Term-Input'].update(output)

                if event2 == "Exit" or event2 == sg.WIN_CLOSED:
                    break

        if event in (sg.WIN_CLOSED, 'Cancel'):
            break

    window.close()

if __name__ == "__main__":
    GUI()