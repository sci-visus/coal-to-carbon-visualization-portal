# Coal To Carbon Visualization Portal



Repository for the code for the visualization portal.

This data portal automaticly makes avalible data visulizations and interactive data visulizations from Juypter Notebook stored on a GitHub repository. It automates the process of going from Juypter Notebook code to an easily sharable data visulization. 

It accomplishes this using Bokeh servers and Git Python.

This code generates a data portal using the flask web framework. It runs a script that reads in Juypter Notebooks from a GitHub repository and then servers the bokeh servers automaticly. A pipe is run between the flask app and the script to pass the list of running notebooks to the data portal. This allows the data portal to automaticly allow any notebook uploaded to the repo to be viewed and interacted with.

Setting up the data portal to run on a Ubuntu server:

```
sudo apt-get update -y
sudo apt-get install -y python3-pip python3-venv

git clone https://github.com/sci-visus/coal-to-carbon-visualization-portal
cd coal-to-carbon-visualization-portal
```

Set up a virtual enviroment:

```
cd flask_app
python3 -m venv venv
source venv/bin/activate
python3 -m pip install -r requirements.txt
```

Edit the `config.yaml` file and change as needed

```

# do the first clone, change as needed
git clone https://github.com/okoppe/Juypter-Notebook-Repo /tmp/Juypter-Notebook-Repo

# before running allow some port range, e.g
sudo ufw allow 5000:6000/tcp

# run the flask app
cd flask_app
source venv/bin/activate

# this may be helpful to release old processes
# sudo killall python3

./run.sh
```

You may be prometed to enter your sudo password.

6. Navigate to the url for your local host (should be outputed in the terminal)
