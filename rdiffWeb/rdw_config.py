#!/usr/bin/python

class SettingsError:
   def __str__(self):
      return "Invalid configuration file syntax"
   
class ParameterError:
   def __str__(self):
      return "Invalid parameters"

def getConfigFile():
   settingsFiles = ["rdw.conf", "/etc/rdiffweb/rdw.conf" ] # TODO: there *has* to be a better way to get the /etc config file path...
   for settingsFile in settingsFiles:
      if os.access(settingsFile, os.F_OK):
         return settingsFile
   return ""
   
def getDatabasePath():
   if os.access("/etc/rdiffweb/rdw.conf", os.F_OK):
      return "/etc/rdiffweb/rdw.db"
   return "rdw.db"
   

import os, re
def getConfigSetting(settingName, settingsFile = None):
   if ('=' in settingName): raise ParameterError
   if settingsFile == None:
      settingsFile = getConfigFile()
   if (not os.access(settingsFile, os.F_OK)): return ""
   settingsStrings = open(settingsFile, "r").readlines()
   for setting in settingsStrings:
      setting = re.compile("(.*)#.*").sub(r'\1', setting)
      setting = setting.rstrip()
      setting = setting.lstrip()
      if not setting: continue
      if not '=' in setting:
         raise SettingsError

      splitSetting = setting.split('=')
      if not len(splitSetting) == 2:
         raise SettingsError

      if splitSetting[0].lower() == settingName.lower(): # Lower-case both vars for case-insensitive compare
         return splitSetting[1]

   return ""

##################### Unit Tests #########################

import unittest
class configFileTest(unittest.TestCase):
   """Unit tests for the getConfigSetting() function"""
   goodConfigText = """ #This=is a comment
   SpacesValue=is a setting with spaces
   spaces setting=withspaces
   CommentInValue=Value#this is a comment
   NoValue=#This is a setting with no value
   """
   badConfigTexts = ['This#doesnt have an equals', 'This=more=than one equals']
   configFilePath = "/tmp/rdw_config.conf"

   def writeGoodFile(self):
      file = open(self.configFilePath, "w")
      file.write(self.goodConfigText)
      file.close()

   def writeBadFile(self, badSettingNum):
      self.writeGoodFile()
      file = open(self.configFilePath, "w")
      file.write(self.badConfigTexts[badSettingNum])
      file.close()


   def tearDown(self):
      if (os.access(self.configFilePath, os.F_OK)):
         os.remove(self.configFilePath)

   def testBadParms(self):
      value = getConfigSetting("setting", "/tmp/rdw_bogus.conf")
      assert(value == "")
      self.writeGoodFile()
      try:
         getConfigSetting("setting=", "/tmp/rdw_config.conf")
      except ParameterError: pass
      else: assert(False)

   def testSpacesInValue(self):
      self.writeGoodFile()
      assert(getConfigSetting("SpacesValue", "/tmp/rdw_config.conf") == "is a setting with spaces")

   def testSpacesInSetting(self):
      self.writeGoodFile()
      assert(getConfigSetting("spaces setting", "/tmp/rdw_config.conf") == "withspaces")

   def testCommentInValue(self):
      self.writeGoodFile()
      assert(getConfigSetting("CommentInValue", "/tmp/rdw_config.conf") == "Value")

   def testEmptyValue(self):
      self.writeGoodFile()
      assert(getConfigSetting("NoValue", "/tmp/rdw_config.conf") == "")

   def testCaseInsensitivity(self):
      self.writeGoodFile()
      assert(getConfigSetting("commentinvalue", "/tmp/rdw_config.conf") == "Value")

   def testMissingSetting(self):
      self.writeGoodFile()
      assert(getConfigSetting("SettingThatDoesntExist", "/tmp/rdw_config.conf") == "")

   def testBadFile(self):
      self.writeBadFile(0)
      try:
         getConfigSetting("SpacesValue", "/tmp/rdw_config.conf")
      except SettingsError: pass
      else: assert(False)

      self.writeBadFile(1)
      try:
         getConfigSetting("SpacesValue", "/tmp/rdw_config.conf")
      except SettingsError: pass
      else: assert(False)
