import os, logging, subprocess, threading, glob, signal, time, traceback,random, yaml
from flask import Flask, render_template, request, Response, send_from_directory, redirect
from multiprocessing import Process,Queue,Pipe
import bokeh

# global config
config={}

# flask app
app = Flask(__name__)
logger=app.logger

# //////////////////////////////////////////////////////////////
class Notebook:

	# constructor
	def __init__(self, key, filename, port):
		'''
		The Notebook class represents a single juypter notebook.
		A Notebook object has all the information needed to server the notebook to a bokeh server.
		'''
		self.key = key
		self.filename = filename
		self.port = port
		self.thread=None

	# run
	def run(self): 
		'''
		Serves the Bokeh application to the websocket. Starts the server on its on thread.
		'''
		def startServer(self):
			subprocess.call(['python3', '-m', 'bokeh', 'serve',  self.filename, '--port', str(self.port), '--allow-websocket-origin='+config["ip"]+':'+str(self.port)])
			
		self.thread = threading.Thread(target=startServer, args=(self,))
		self.thread.start()

	# shutdown
	def shutdown(self):
		'''
		kill the thread
		'''
		self.thread.kill()

	# getUrl
	def getUrl(self):
		'''
		Getter function to return the link to the Bokeh server.
		'''
		return ('http://'+config["ip"]+':'+str(self.port)+'/'+self.key.replace(".ipynb",""))



# //////////////////////////////////////////////////////////////
class Notebooks:

	# constructor
	def __init__(self):
		'''
		This class represents a colection of Notebook objects that corrispond to the .ipynb files in a git hub repo.
		'''
		self.map = {}

	singleton=None

	@staticmethod
	def getSigleton():
		if Notebooks.singleton is None:
			singleton = Notebooks()
			singleton.updateAll()
			# singleton.trackChangesInBackground()
			Notebooks.singleton=singleton
		return Notebooks.singleton

	# addNotebook
	def addNotebook(self, key, filename):
		if key in self.map: return
		port = random.randint(config["worker-ports"]["from"],config["worker-ports"]["to"]) # TODO: here I am hoping for no collision
		notebook = Notebook(key, filename , port)
		notebook.run()
		self.map[key] = notebook

	# removeNotebook
	def removeNotebook(self, key):
		if key not in self.map: return
		self.map[key].shutdown()
		self.map.pop(key)

	# updateAll
	def updateAll(self):

		files = [os.path.relpath(it,config["local"]) for it in glob.glob(os.path.join(config["local"] + "/**/*.ipynb"),recursive=True)]
		logger.info(f"updateAll {config['local']} {files}")

		# delete files and Notebook objects from the array that have been deleted in the repo
		for key in self.map:
			if key not in files:
				self.removeNotebook(key)

		# Create a new Notebook object for each new .ipynb file
		for key in files:
			self.addNotebook(key, os.path.join(config["local"],key))

	# trackChangesInBackground
	def trackChangesInBackground(self):
		def RunInBackground():
			while True:
				try:
					import git
					g = git.cmd.Git(config["local"])
					g.pull(config["remote"])
					self.updateAll()
				except Exception as ex:
					logger.error(ex)
		threading.Thread(target=self.RunInBackground, args=()).start()

	# getLinks
	def getLinks(self):
		ret={}
		for k,v in self.map.items():
			ret[k]=v.getUrl()
		return ret

# //////////////////////////////////////////////////////////////////////////
def HandleRequest(child_conn):
	child_conn.send(Notebooks.getSigleton().getLinks())
	child_conn.close()

# //////////////////////////////////////////////////////////////////////////
def GetLinks():
	parent_conn,child_conn = Pipe()
	p = Process(target=HandleRequest, args=(child_conn,))
	p.start()
	ret = parent_conn.recv()
	p.join()
	return ret


selected=None

# //////////////////////////////////////////////////////////////////////////
#hone directory
@app.route("/")
def index():
	links=GetLinks()
	return render_template(
		"index.html",  
		links=list(links.keys()), 
		selected=None
	) 

# //////////////////////////////////////////////////////////////////////////
#path for veiwing data set inline
@app.route('/chooseNotebook/<key>', methods = ['POST', 'GET'])
def chooseNotebook(key):
	links=GetLinks()
	return redirect(links[key].replace(".ipynb",""), code=302)


# //////////////////////////////////////////////////////////////////////////
#path for downloading file
@app.route("/downloadNotebook", methods=['GET', 'POST'])
def downloadNotebook():
	notebooks=Notebooks.getSingleton()
	return send_from_directory(
		directory=config["local"], 
		path=notebooks.selected, 
		as_attachment=True)

# //////////////////////////////////////////////////////////////////////////
def LoadConfigFile():
	from yaml.loader import SafeLoader
	with open(os.path.join(os.path.dirname(__file__),'config.yaml')) as f:
		return yaml.load(f, Loader=SafeLoader)
		

# //////////////////////////////////////////////////////////////
if __name__ == "__main__":
	logger.setLevel(logging.INFO)
	config=LoadConfigFile()
	logger.info(f"Notebooks {config}")
	app.run(host="0.0.0.0", port=config["port"], debug=bool(config["debug"]))
