#! /usr/bin/env python
# -*- coding: utf-8 -*-
# 
# version 0.1
# 


import os,time
import socket,struct
import cgi
import uuid

import cherrypy
from cherrypy.lib.static import serve_file

try:
	import android
	_droid_=android.Android()
	_wifi_=_droid_.wifiGetConnectionInfo().result
	print 'SSID : ' + _wifi_['ssid']
	_ip_=_wifi_['ip_address']
	_ip_=socket.inet_ntoa(struct.pack('L',_ip_))
	print 'ip : ' +str(_ip_)
except:
	print 'not android machine'



head="""
<html>
<head>
<title>XaXa Explorer</title>
"""



css=""" 
<style type="text/css">
/* More info here : http://www.red-team-design.com/css3-ordered-list-styles */
body {
    margin: 40px auto;
    width: 500px;
}

ol{
	counter-reset: li; /* Initiate a counter */
	list-style: none; /* Remove default numbering */
	*list-style: decimal; /* Keep using default numbering for IE6/7 */
	font: 15px 'trebuchet MS', 'lucida sans';
	padding: 0;
	margin-bottom: 4em;
	text-shadow: 0 1px 0 rgba(255,255,255,.5);
}

ol ol{
	margin: 0 0 0 2em; /* Add some left margin for inner lists */
}

.rounded-list a.file{
	position: relative;
	display: block;
	padding: .4em .4em .4em 2em;
	*padding: .4em;
	margin: .5em 0;
	background: #ddd;
	color: #444;
	text-decoration: none;
	border-radius: .3em;
	transition: all .3s ease-out;        
}

.rounded-list a.directory{
	position: relative;
	display: block;
	padding: .4em .4em .4em 2em;
	*padding: .4em;
	margin: .5em 0;
	#background: #EBB946;
	background: #879DF5;
	color: #444;
	text-decoration: none;
	border-radius: .3em;
	transition: all .3s ease-out;        
}

.rounded-list a:hover{
	background: #eee;
}
# .rounded-list a:hover:before{
# transform: rotate(360deg); 
# }

.rounded-list a.directory:before{
	content: counter(li);
	counter-increment: li;
	position: absolute;        
	left: -1.3em;
	top: 50%;
	margin-top: -1.3em;
	 #background: #D49504;
	background: #788CDE;
	height: 2em;
	width: 2em;
	line-height: 2em;
	border: .3em solid #fff;
	text-align: center;
	font-weight: bold;
	border-radius: 2em;
	transition: all .3s ease-out;
}
.rounded-list a.file:before{
	content: counter(li);
	counter-increment: li;
	position: absolute;        
	left: -1.3em;
	top: 50%;
	margin-top: -1.3em;
	background: #87ceeb;
	height: 2em;
	width: 2em;
	line-height: 2em;
	border: .3em solid #fff;
	text-align: center;
	font-weight: bold;
	border-radius: 2em;
	transition: all .3s ease-out;
}
</style>

"""


upload="""
</head>
<body>
            <h2>Upload a file</h2>
            <form action="/upload" method="post" enctype="multipart/form-data">
            filename: <input type="file" name="myFile" /><br />
            <input type="submit" />
            </form>
            <h2>Download a file</h2>
<h2>{0}</h2>
<ol class="rounded-list">
"""

hlist="""
<li><a class='{0}' href='{1}'>{2}</a></li>

"""
foot="""
</ol>
</body>
</html>
"""

dl_dir="/storage/sdcard0/Download/"

class field(cgi.FieldStorage):
    def make_file(self,binary=None):
        self.t= file(os.path.join(dl_dir,self.filename),'wb')
        return self.t


def nobody():
    cherrypy.request.process_request_body = False


cherrypy.tools.nobody=cherrypy.Tool('before_request_body',nobody)


_base_dir_=os.getcwd().split(os.path.sep)[0]+os.path.sep
print os.getcwd()
class Explore(object):

	def default(self,*args):
		temp_walk=os.path.join(_base_dir_,os.path.sep.join(args))
		if os.path.isdir(temp_walk):
			try:
				templst=os.listdir(temp_walk)
			except:
				return 'impossible de lister le repertoire....'
		elif os.path.isfile(temp_walk):
			return serve_file(temp_walk,"application/x-download","attachement")
		else:
			return 'ni fichier ni repertoire....'
		#templst.sort()
		bod=''.join(sorted([hlist.format('directory','/'+'/'.join(args+(x,)),x) \
									if os.path.isdir('/'+'/'.join(args+(x,))) \
									else hlist.format('file','/'+'/'.join(args+(x,)),x) \
								for x in templst]))
		return head+css+upload.format(temp_walk)+bod+foot
	default.exposed = True
    
	@cherrypy.tools.nobody()
	def upload(self, *args):
		out = """<html>
	<body>
		myFile Content-Length: %s<br />
		name: %s<br/>
		</body>
	</html>"""
		print args
		req = cherrypy.request
		fieldStorage = field(fp = req.rfile,headers=req.headers,
									environ={'REQUEST_METHOD':'POST'},
									keep_blank_values=True)
		print fieldStorage['myFile'].filename
		return out % (req.headers['Content-Length'],fieldStorage['myFile'].filename)
	upload.exposed = True



cherrypy.server.socket_host="0.0.0.0"
if __name__ == '__main__':
	cherrypy.quickstart(Explore())
