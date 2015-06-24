http://sodesne.com/blog/2012/11/26/publishing-a-flask-app-with-azure

Publishing a Flask App with Azure

I've recently given Microsoft's Azure Cloud Framework a try and have written down the steps I followed to successfully deploy a python Flask app on an Azure VM.

To set up an account with Azure, go here. Microsoft is currently offering a 90 day free trial of their cloud services.

A bit of disclaimer before we get started - Azure's services are in preview and may change in the future. Also, I'm not a security expert and am giving directions for a "hello world" type app only. If you need to make secure or critical deployments, you will need more in-depth guidance than this article provides.

Setting up the VM

Once you have an account, select 'virtual machines' from the bar on the left and then click on the 'new' button in the bottom left corner.
This image shows my setup, with one VM already running in place (I've hidden the machine name and URL)
This image shows my setup, with one VM already running in place (I've hidden the machine name and URL)

For this demo, the Quick Create options will work just fine. From the drop down menus, select Ubuntu Server 12.04 LTS, and for size choose Extra Small. The DNS name is the url you will use to access the machine. In this example, I've used 'demoflaskapp'. To access the server, I'll navigate to demoflaskapp.cloudapp.net.

You can use any password you'd like, but note that at this point, there is not a way to reset this password if you lose it - you'll just have to rebuild the machine.

You can use any region you'd like in the location drop down, generally it makes the most sense to use a region close to you.
Quick Create Menu.
Quick Create Menu.

Once you select "create virutal machine", the server should appear in your virtual machines list. The status will read "Starting(Provisioning)". It may take a few minutes to get up and running. Once this is finished, the status will show as "Stopped". You can hit the start button on the bottom bar - in a few moments your app will appear as "Running".
Your new running VM.
Your new running VM.

Next, as the image above shows, click on the machine name. This will open a dashboard view that will show you information on your machine's activity. Since the machine was just created, the graphs will be blank.
The Dashboard View.
The Dashboard View.

There are two other tabs you can access from this view, "Endpoints" and "Configure". Let's go to Endpoints.
Endpoints View.
Endpoints View.

Endpoints are the connections that Microsoft's cloud infrastructure allows between your virtual machine and the outside world. By default, all connections other than SSH are blocked. Since we want to use this machine as a web server, we'll need to open up port 80 for HTTP access. Click on the "Add Endpoint" (+) icon on the bottom, and when you are prompted, select "Add Endpoint". You can name the endpoint whatever you want (I called it HTTP). Leave the protocol on TCP. For "Public Port" and "Private Port", enter the number 80.
Successfully created a HTTP Endpoint.
Successfully created a HTTP Endpoint.

If you can see an entry HTTP similar to the image above, you're all set! It will take a few minutes for the service to turn on.

At this point, we've done everything we need to do from the Microsoft front end.

Configure the Ubuntu VM

You will need to use SSH to log in to the VM. Earlier, I set up my VM with the default user "azureuser" and machine name "demoflaskapp", I'll log in via a terminal with the command "ssh azureuser@demoflaskapp.cloudapp.net".

If you are on a Windows machine, you can use PuTTY to make a SSH connection.

Here’s what the initial log-on looks like:
Initial SSH Login.
Initial SSH Login.

We are going to set up a Flask/Gunicorn/Nginx stack that's managed via Ubuntu's Upstart tools. There are lots of other ways to serve Flask on a virtual machine, but they will not be discussed in this guide.

Before we get started, go to your VM's url in your web browser. For me, that's http://demoflaskapp.cloudapp.net. You should get an error message from your browser - that is expected.

Install System Dependencies

The required Python modules will be installed via PIP.

Update your apt-get packages:

sudo apt-get update
Install git:

sudo apt-get install git
Install pip:

sudo apt-get install python-pip
Install Flask:

sudo pip install flask
Install Gunicorn:

sudo pip install gunicorn
Install Requests:

sudo pip install requests
Install nginux:

sudo apt-get install nginx
At this point, even though we've installed the necessary components, browsing to your VM's url will still fail -- the installed components still haven't been configured.

Configure nginx

We're going to set up a bare-bones nginx server. There are many ways to configure nginx - I'm going to show you one. Also, this tutorial skips over the details of how to edit files in Linux - that is on you. If you've never edited files in Linux before, check out nano.

I'm calling the configuration file flask-app - you can name it whatever you want. Make sure to update the server_name line to match your VM's name.

Stop the nginx service:

sudo /etc/init.d/nginx stop
Remove the default site configuration:

sudo rm /etc/nginx/sites-enabled/default
Create a file (with sudo) at /etc/nginx/sites-available/flask-app with the following contents:

server {
  listen 80;
  server_name demoflaskapp.cloudapp.net;
  access_log  /var/log/nginx/demoflaskapp.log;

location / {
    proxy_pass http://127.0.0.1:8000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
  }
}
Link this file to the sites-available folder:

sudo ln -s /etc/nginx/sites-available/flask-app /etc/nginx/sites-enabled/flask-test
Start the nginx service:

sudo /etc/init.d/nginx start
Moment of truth - at this point, navigating to your VM's URL should show you a nginx error message. This indicates that nginx is running, but the other components (gunicorn/flask) are not.
A Successful Error Message.
A Successful Error Message.

Set up Flask

Now, let's get a basic Flask app running.

Create a project directory:

cd ~
mkdir demoFlask
Create an app.py file in your project directory with the following contents:

from flask import Flask

app = Flask(__name__)

@app.route('/')
def index():
    return "<h1>This flask app is running!</h1>"

if __name__ == '__main__':
    app.run(port=8000)
You'll note that we're setting the app to run on port 8000. The default for most flask demos is 5000, but we configured ngnix above to listen for a server on port 8000.

Now run the Flask app manually:

cd ~/demoFlask
python ./app.py
If you see the message "running on http://127.0.0.1.8000", you're good! Go to your VM's URL to admire your awesome app.
The Running Flask App.
The Running Flask App.

Now we have verified that 1) ngnix is running and 2) flask is running. You will notice above that we launched Flask via the command line. Flask has a built-in web server that's suitable for development, but since we are going to the trouble to put the app up on a VM, we are also going to set it up with a proper HTTP server.

Set Up Gunicorn/Upstart

gunicorn is already more or less set up on your VM, since we have installed it via PIP. You can launch it via the terminal just like you launched Flask directly. (Type Ctrl-C to stop the python app if it is already running).

Test gunicorn:

gunicorn app:app -b 127.0.0.1:8000
This command will launch gunicorn and have it serve the Flask app you made on port 8000. If you launch a web browser after you run this, it shouldn't look any different in your browser from the previous test.

What we want to do is set our server up so the Flask app is served automatically whenever the server is booted up. To do this we'll use Upstart. If you want to look at another method, Supervisor is a nice alternative to upstart.

We need to build a script that tells upstart when and how to launch gunicorn.

Create a file demoflask in /etc/init/demoflask.conf (as sudo) with the following contents:

description "Launch my Flask Demo App via gunicorn"
start on startup
chdir /home/azureuser/demoFlask
exec gunicorn app:app -b 127.0.0.1:8000
This script instructs the Upstart manager to change to your project directory and launch gunicorn with the same command we used in our test.

Now, test your script by trying to start the gunicorn process:

sudo start demoflask
You should see a message like "demoflask start/running". When you reload your browser pointed at your VM's URL, it will serve the Flask app correctly, even though you're not explicitly running a server from the terminal.

One note about this configuration - unlike the development server, by default gunicorn does not update when you modify a file. This means if you make changes to app.py and reload your browser, it will not update.
Issue the command:

sudo reload demoflask
To get the web server to look at your latest code.

Final Test

As a final test, let's reboot the VM and make sure the app is still served properly.

Go back to the Azure dashboard. (As an aside, if you click on your VM name and view the dashboard, you'll see some activity.)

At the bottom of the window, you will see a restart button. Press that, and then try to view your Flask app -- once again you will get an error (no response) back from the browser.
Reset your VM.
Reset your VM.

Once the server is back up and running according to the dashboard, reload the Flask browser window and you will see your hello world message again.

I hope this was a useful tutorial - any comments or questions, please let me know. You can reach me via Twitter at @bdfife or here.

Want more information on Azure/Python? Check out the Azure/Python page.