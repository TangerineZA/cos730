# PURPOSE OF SERVER COMPONENT:
# - provide download server capabilities
# - enable processing of collaboration service

from flask import Flask, render_template, request, Response, jsonify, send_file
import json
import unittest

class User:
    def __init__(self, username : str = "", password : str = "") -> None:
        self.username : str = username
        self.password : str = password

    def update_details(self, username : str = "", password : str = "") -> bool: # TODO add validation
        self.username : str = username
        self.password : str = password

class OnlineFile:
    def __init__(self, name, permitted_users, content = "") -> None:
        self.name = name
        self.content = content
        self.permitted_users = permitted_users

    def overwrite(self, content):
        self.content = content
        return content
    
    def get_content(self):
        return self.content

class FileList:
    def __init__(self) -> None:
        self.filelist : list[OnlineFile] = []
    
    def get_file_contents(self, filename : str) -> str:
        for i in len(self.filelist):
            if self.filelist[i].name == filename:
                return self.filelist[i].content
            
        print("File not found in list!")
        return None

    def get_file(self, filename : str) -> OnlineFile:
        for i in len(self.filelist):
            if self.filelist[i].name == filename:
                return self.filelist[i]
            
        print("File not found in list!")
        return None

app = Flask(__name__)
fl = FileList()
ul : list[User] = []

@app.route('/')
def main_page():
    return render_template('webpage.html')

@app.route('/download/')
def post_latest():
    try:
        send_file('update.exe')
    except:
        print("error!")
        return Response(
            "Server error", status=500
        )

@app.route('/collaborate/', methods=['GET', 'POST'])
def collab():
    # GET collaborate sends latest version in JSON form
    if request.method == 'GET':
        try:
            if request.form['username'] in file.permitted_users:
                return jsonify({'content': file.content})
        except:
            print("Network error A")
        file = fl.get_file(request.form['filename'])
    
    # POST collaborate updates access
    elif request.method == 'POST':
        json_file = request.get_json()
        request_dict = json.loads(json_file)
        file = fl.get_file(request_dict['filename'])
        if request.form['username'] in file.permitted_users:
            try:
                file.overwrite(request.form['content'])
            except:
                print("Network error B")

@app.route('/register/', methods=['POST'])
def add_user():
    try:
        json_file = request.get_json()
        request_dict = json.loads(json_file)
        ul.append(request_dict['username'])
    except:
        print("error!")
        return Response(
            "Server error", status=500
        )

@app.route('/authenticate/', methods=['GET'])
def auth_user():
    try:
        test_user = User(request.form['username'], request.form['password'])    
        if request.method == 'GET':
            for user in ul:
                if user.username == test_user.username:
                    if user.password == test_user.password:
                        return Response("Verified!", status=200)
        
        return Response("Incorrect!", status=400)
    except:
        print('error')
        return Response("Error!", status=500)

if __name__ == 'main':
    app.run()