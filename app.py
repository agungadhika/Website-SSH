from flask import Flask, render_template, request
import paramiko

app = Flask(__name__)


servers = [
    {"name": "Server 1", "host": "host", "username": "username", "password": "password"},
    {"name": "Server 2", "host": "host2", "username": "username2", "password": "password2"},
]

alias_commands = {
    "Server 1": {
        "ls": "ls -l",
        "testing": '''
            cd /home/agung/ &&
            touch testing.txt &&
            '''
    },
    "Server 2": {"ls": "ls -a", "whoami": "whoami"}
}


@app.route('/')
def index():
    return render_template('index.html', servers=servers, alias_commands=alias_commands)

@app.route('/execute_command/<server_name>/<command_name>')
def execute_command(server_name, command_name):
    server = next((s for s in servers if s["name"] == server_name), None)

    if server:
        real_command = alias_commands.get(server_name, {}).get(command_name)

        if real_command:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            try:
                ssh.connect(server['host'], username=server['username'], password=server['password'])
                stdin, stdout, stderr = ssh.exec_command(real_command)
                result = stdout.read().decode('utf-8')
            except Exception as e:
                result = str(e)
            finally:
                ssh.close()

            return render_template('result.html', result=result)

    return "Server or command not found."

if __name__ == '__main__':
    app.run(debug=True)