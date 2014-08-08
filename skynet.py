#!/usr/bin/env python
#
#

# set some variables

base_url = 'https://cloud.skytap.com'
user = 'skynet@fulcrum.net'
token = '55b5e1a75ce9a122db3c976d161f96b15b5eb825'

working_dir = '/Users/thewellington/Development/skynet'              # this is the path to the skynet.py file
control_dir = '/Users/thewellington/Development/skytap-control'      # this is the path to the skytap-control directory
temp_dir = '/tmp'


# import necessary modules

import sys
import traceback
import getopt
import json

try:
  import requests
except ImportError:
  sys.stderr.write("You do not have the 'requests' module installed.  Please see http://docs.python-requests.org/en/latest/ for more information.")
  exit(1)



############################################################################ 
#### begin api interactions


def _api_get(url):
    url, name, passwd = url, user, token
    
    requisite_headers = { 'Accept' : 'application/json',
                          'Content-Type' : 'application/json'
    }
    auth = (name, passwd) 
    
    response =  requests.get(url, headers=requisite_headers, auth=auth)
    
    return response.status_code, response.text


def _api_put(argv):
    url, name, passwd = argv[0], argv[1], argv[2]
    
    requisite_headers = { 'Accept' : 'application/json',
                          'Content-Type' : 'application/json'
    }
    auth = (name, passwd) 
 
    if len(argv) > 3:
        data = load_file(argv[3])
    else:
        data = None
    
    response =  requests.put(url, headers=requisite_headers, auth=auth, data=data)
    
    return response.status_code, response.text
    

def _api_post(argv):
    url, name, passwd = argv[0], argv[1], argv[2]
    
    requisite_headers = { 'Accept' : 'application/json',
                          'Content-Type' : 'application/json'
    }
    auth = (name, passwd) 
 
    if len(argv) > 3:
        data = load_file(argv[3])
    else:
        data = None
    
    response =  requests.post(url, headers=requisite_headers, auth=auth, data=data)
    
    return response.status_code, response.text


def _api_del(argv):
    url, name, passwd = argv[0], argv[1], argv[2]
    
    requisite_headers = { 'Accept' : 'application/json',
                          'Content-Type' : 'application/json'
    }
    auth = (name, passwd) 
    
    response =  requests.delete(url, headers=requisite_headers, auth=auth)
    
    return response.status_code, response.text


def rest_usage():
    print "usage: rest [put|get|post|delete] url name passwd"
    sys.exit(-1)

cmds = {
    "GET": _api_get, 
    "PUT": _api_put, 
    "POST": _api_post,
    "DELETE": _api_del
    }

def load_file(fname):
  with open(fname) as f:
    return f.read()

def rest(req, url, user, token):

#     if len(argv) < 4:
#         rest_usage()
        
    if 'HTTPS' not in url.upper():
        print "Secure connection required: HTTP not valid, please use HTTPS or https"
        rest_usage()       
        
    cmd = req.upper()
    if cmd not in cmds.keys():
        rest_usage()

    status,body=cmds[cmd](url)
    print
    if int(status) == 200:
        json_output = json.loads(body)
        print json.dumps(json_output, indent = 4)        
    else:
        print "Oops!  Error: status: %s\n%s" % (status, body)
        print
        
############################################################################ 
#### begin custom functions

def get_configurations():
  body = rest('get', base_url+'/configurations', user, token)
  json_output = json.loads(body)
  #print json_output
  #print json.dumps(json_output, indent = 4)

  l = []
  for j in json_output:
    l.append(j.get('id'))

  print l
      

############################################################################ 
#### begin interface items


def usage(exitcode):

  usage="""
##########    Welcome to Skynet    ##########

At this time Skynet takes two arguments at most.  Here are your options
  
  -h --help     Produces this help file
  -a --action   Indicates the action you wish to take
  -s --scope    Defines the scope of the action(s)
  
EXAMPLES:

skynet -a suspend -s limited
  
"""

  try:
    exitcode
  except NameError:
    print usage
    sys.exit(-1)
  else:
    print usage
    sys.exit(exitcode)

 
# argument parser
def ui(argv):
  
# define variables to be used by getopts and sent them to null
  action = ''
  scope = ''
  
#  print 'ARGV     :', sys.argv[1:]
  
  try:
    options, remainder = getopt.gnu_getopt(sys.argv[1:], 'a:hs:t', ['help',
                                                          'action=',
                                                          'scope=',
                                                          ])
                                            
  except getopt.GetoptError:
    usage()
    sys.exit(2)


#  print 'OPTIONS    :', options

  for opt, arg in options:
    if opt in ('-h', '--help'):
      print usage
      sys.exit()

    elif opt in ( '-a', '--action' ):
      action = arg
    
    elif opt in ( '-s', '--scope' ):
      scope = arg
      
    elif opt in ( '-t' ):
      rest('get', base_url+'/configurations', user, token)
    
#   print 'ACTION   :', action
#   print 'SCOPE      :', scope
#   print 'REMAINING  :', remainder




 
# call main
if __name__=='__main__':

  ui(sys.argv[1:]) 