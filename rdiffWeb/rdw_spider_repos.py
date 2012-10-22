#!/usr/bin/python

import os
import db
import rdw_helpers
import librdiff
import rdw_config
import time
import threading

# Returns pid of started process, or 0 if no process was started
def startRepoSpiderThread(killEvent):
   newThread = spiderReposThread(killEvent)
   newThread.start()

class spiderReposThread(threading.Thread):
   def __init__(self, killEvent):
      self.killEvent = killEvent
      threading.Thread.__init__(self)
      
   def run(self):
      spiderInterval = rdw_config.getConfigSetting("autoUpdateRepos")
      if spiderInterval:
         spiderInterval = int(spiderInterval)         
         while True:
            findReposForAllUsers()
            self.killEvent.wait(60*spiderInterval)
            if self.killEvent.isSet():
               return
      

def _findRdiffRepos(dirToSearch, outRepoPaths):
   dirEntries = os.listdir(dirToSearch)
   if librdiff.rdiffDataDirName in dirEntries:
      outRepoPaths.append(dirToSearch)
      return

   for entry in dirEntries:
      entryPath = rdw_helpers.joinPaths(dirToSearch, entry)
      if os.path.isdir(entryPath) and not os.path.islink(entryPath):
         _findRdiffRepos(entryPath, outRepoPaths)


def findReposForUser(user, userDBModule):
   userRoot = userDBModule.getUserRoot(user)
   repoPaths = []
   _findRdiffRepos(userRoot, repoPaths)

   def stripRoot(path):
      if not path[len(userRoot):]:
         return "/"
      return path[len(userRoot):]
   repoPaths = map(stripRoot, repoPaths)
   userDBModule.setUserRepos(user, repoPaths)


def findReposForAllUsers():
   userDBModule = db.userDB().getUserDBModule()
   if not userDBModule.modificationsSupported(): return
   
   users = userDBModule.getUserList()
   for user in users:
      findReposForUser(user, userDBModule)

