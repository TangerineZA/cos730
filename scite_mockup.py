import PySimpleGUI as sg
import tkinter as tk
from tkinter import filedialog
import os

import requests
import json

from abc import abstractmethod
import subprocess
import language_tool_python

SERVER_ADDRESS = "127.0.0.1:5000"

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
        self.tool= language_tool_python.LanguageTool('en-US')

    def check(self, text) -> list:
        mistakes = self.tool.check(text)
        for mistake in mistakes:
            print(mistake)
        return mistakes

    def fix(self, text) -> str:
        return self.tool.correct(text)

class Compiler:
    @abstractmethod
    def check(self, text):
        pass

    @abstractmethod
    def compile(self):
        pass

    @abstractmethod
    def run(self, text):
        pass

class Java_compiler(Compiler):
    def compile(self):
        java_compiler_output = subprocess.check_output("javac *.java", shell=True).decode('utf-8')
        print('COMPILER OUTPUT -------------------------\n' + java_compiler_output + '-------------')
        return java_compiler_output

    def run(self, filename):
        pass

class Collaboration_worker:
    def __init__(self) -> None:
        self.user : User

    def add_user(self, username : str):
        user_json = {'username': username}
        address = SERVER_ADDRESS + "/register/"
        response = requests.post(url=address, json=user_json)

    def update_user(self, user):
        self.user = user

    def sync(self):
        payload = {"user": self.user.username}
        response = requests.get(SERVER_ADDRESS + '/collaborate/')
        data = response.json()
        response_dict = json.loads(data)
        text = response_dict['content']
        return data
    
class Temp_file:
    def __init__(self, name="default", content="") -> None:
        self.name = name
        self.content = content
        self.users = []

    def add_user(self, user):
        self.users.append(user)

class Temp_server:
    def __init__(self) -> None:
        self.file_list : list[Temp_file] = []

    def add_file(self, name, content="", user = None):
        tfile = Temp_file(name, content)
        if user != None:
            tfile.add_user(user)
        self.file_list.append(tfile)


    def get_file(self, filename, username):
        for file in self.file_list:
            if file.name == filename:
                if username in file.users:
                    return file.content


class GUI:
    sg.theme('DefaultNoMoreNagging')
    current_user = User()

    menu_def = [
        ['File', ['Open', 'Save', 'Save As']], 
        ['Compiler', ['Compile Java', 'Run Java']], 
        ['Terminal', ['Open in SciTE', 'Open in system shell']], 
        ['Collaborate', ['Login', 'Invite user', 'Sync', 'End session']], 
        ['Checker', ['Language check', 'Fix language']]]
    # All the stuff inside your window. This is the sg magic code compactor...
    layout =    [[sg.Menu(menu_def)],
                [sg.Multiline("", key='textarea',
                expand_x=True, expand_y=True)]]

    # Create the Window
    window = sg.Window('SciTe mockup', layout, size=(1280, 720), resizable=True)
    # Event Loop to process "events"
    while True:             
        tserver = Temp_server()
        event, values = window.read()
        collab_worker = Collaboration_worker()
        filepath = None

        filename = "default"

        if event:
            print(event)
            
        if event == 'Login':
            username = sg.popup_get_text("Please enter your username:")
            password = sg.popup_get_text("Please enter your password:")
            current_user.update_details(username=username, password=password)

            tserver.add_file('default', values['textarea'], username)

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

        if event == 'Open in SciTE':
            second_layout = [[sg.Multiline('', key='term-out', disabled=True, expand_x=True, expand_y=True)],
                             [sg.Multiline('Input', key='term-in'), sg.Button('Run')]]
            second_window = sg.Window("Terminal", second_layout, size=(500,750))
            while True:
                event2, values2 = second_window.read()

                if event2 == 'Run':
                    print(values2['term-in'])
                    output = subprocess.check_output(values2['term-in'], shell=True).decode('utf-8')
                    print(output)
                    second_window['term-out'].update(output)

                if event2 == "Exit" or event2 == sg.WIN_CLOSED:
                    break

        if event == 'Language check':
            gc = Grammar_checker()
            mistakes = gc.check(values['textarea'])
            mistake_text = ''

            for mistake in mistakes:
                print(mistake)
                mistake_text = mistake_text + mistake.__str__()

            second_layout = [[sg.Multiline(mistake_text, key='term-in', expand_x=True, expand_y=True)], 
                             [sg.Button('Fix'), sg.Button('Close')]]
            second_window = sg.Window("Mistakes", second_layout, size=(700, 700))
            print('Window spawned')
            while True:
                event2, values2 = second_window.read()

                if event2 == 'Fix':
                    fixed = gc.fix(values['textarea'])
                    window['textarea'].update(fixed)
                    break

                if event2 == "Close" or event2 == sg.WIN_CLOSED:
                    break

        if event == 'Sync':
            # window['textarea'].update(collab_worker.sync())
            window['textarea'].update(
                tserver.get_file(filename, current_user.username)
            )

        if event == 'Compile Java':
            try:

                jc : Java_compiler = Java_compiler()

                second_layout = [[sg.Multiline('', key='term-out', disabled=True, expand_x=True, expand_y=True)],
                                 [sg.Button("Compile...")]]
                second_window = sg.Window("Compiler Output", second_layout, size=(500,750))
                while True:
                    event2, values2 = second_window.read()

                         
                    if event2 == "Compile...":
                        output = jc.compile()
                        second_window['term-out'].update(output)  

                    if event2 == "Exit" or event2 == sg.WIN_CLOSED:
                        break
            except:
                print("An error occurred!")


        if event in (sg.WIN_CLOSED, 'Cancel'):
            window.close()
            exit()

if __name__ == "__main__":
    GUI()