#! /usr/bin/env python3
import re
import requests
import sys
import json
from getpass import getpass

class CommandNotFound(Exception):
    """docstring for CommandNotFound"""
    def __init__(self, message=None):
        #super(CommandNotFound, self).__init__(message)
        if message is None:
            self.message = "Command not found"
        else:
            self.message = message

    def __str__(self):
        return repr(self.message)


class ASClient:

    HOST = "127.0.0.1"
    PORT = "8000"
    username = None
    passwd = None

    def __init__(self):
        pass

    def _authentication(self):
        self.username = 'admin'#input('username: ')
        self.passwd = 'galaxy@123'#getpass("password: ")

    def _request(self, method, uri, data = None):
        uri = 'http://{}:{}/api/v1/{}'.format(self.HOST, self.PORT, uri)
        auth = (self.username, self.passwd)
        headers = {'Content-Type': 'application/json', 'Accept': 'application/json; indent=4'}

        reponse = None
        if method == 'get':
            response = requests.get(uri, auth=auth, headers=headers, data=data)
        elif method == 'post':
            response = requests.post(uri, auth=auth, headers=headers, data=data)
        elif method == 'put':
            response = requests.put(uri, auth=auth, headers=headers, data=data)
        elif method == 'delete':
            response = requests.delete(uri, auth=auth, headers=headers, data=data)
        return response

    def _run(self):
        if self.username is None:
            self._authentication()
        while True:
            try:
                command = input('{}@autoscaling -> '.format(self.username))
                command = command.split()
                command_name = command[0]
                if command_name.startswith("_"):
                    raise CommandNotFound()
                attr = getattr(self,command_name)
                if callable(attr):
                    attr(command)
                else:
                    raise CommandNotFound()
            except CommandNotFound as e:
                print("Error: " + str(e))
            except Exception as e:
                print("Error: Unknow error!")


    def app(self, command):
        if command[1] == "--all":
            response = self._request("get","apps")
            print(response.text)

        elif command[1] == '--name':
            response = self._request("get","apps/"+command[2])
            print(response.text)

        elif command[1] == "create":
            if command[2] == '--file':
                content = self._get_content_file(command[3])
                response = self._request("post", "apps", content)
                print(response.text)
            else:
                pass

        elif command[1] == 'delete':
            if command[2] == '--name':
                response = self._request("delete","apps/"+command[3])
                print(response.text)

        elif command[1] == 'policy':
            if command[2] == '--list':
                response = self._request("get","apps/{}/policies".format(command[3]))
                print(response.text)
            elif command[2] == '--delete':
                response = self._request("delete","apps/{}/policies/{}".format(command[3],comand[4]))
                print(response.text)
            elif command[2] == '--add':
                if command[4] == '--file':
                    content = self._get_content_file(command[5])
                    response = self._request("post", "apps/{}/policies".format(command[3]), content)
                    print(response.text)
                else:
                    pass


    def _get_content_file(self, file_name):
        with open(file_name, 'r') as file_data:
            return content = file_data.read()

    def exit(self, command):
        sys.exit()


def main():
    as_client = ASClient()
    as_client._run()

if __name__ == '__main__':
    main()
