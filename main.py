from functools import reduce
import seleniumwire.undetected_chromedriver.v2 as seleniumWireWebdriver
import undetected_chromedriver.v2 as webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import os
import time
import json
from sys import platform

if platform == 'linux':
    seperator = str(os.path.sep)
else:
    seperator = str(os.path.sep) + str(os.path.sep)

_E = False
_D = 'VARIABLES'
_C = 'utf-8-sig'
_B = 'data.ini'
_A = True


def getParentFolder():
    from sys import platform
    if platform == 'win32':
        A = '\\'
        import sys, pathlib
        if getattr(sys, 'frozen', _E):
            current_direct = str(pathlib.Path(sys.executable).parent.resolve()) + A;parantez = str(current_direct)[:-1][::-1].find(A);parentFolder = str(current_direct)[:-1][::-1][parantez:][::-1]
        elif __file__:
            current_direct = str(pathlib.Path(__file__).parent.resolve()) + A;parantez = str(current_direct)[:-1][::-1].find(A);parentFolder = str(current_direct)[:-1][::-1][parantez:][::-1]
        return parentFolder
    elif platform == 'linux':
        from pathlib import Path
        parentFolder = Path(Path.cwd()).parent
        parentFolder = str(parentFolder) + '/'
        return str(parentFolder)

parentFolder = getParentFolder()
class ChromeWithPrefs(webdriver.Chrome):
    def __init__(self, *args, options=None,useData=True,**kwargs):
        if options:
            self.handle_prefs(options,useData)
        super().__init__(*args, options=options, **kwargs)
        if useData:
            self.keep_user_data_dir = True
        else:
            self.keep_user_data_dir = False

    @staticmethod
    def handle_prefs(options,useData = True):
        if prefs := options.experimental_options.get("prefs"):
            def undot_key(key, value):
                if "." in key:
                    key, rest = key.split(".", 1)
                    value = undot_key(rest, value)
                return {key: value}
            undot_prefs = reduce(lambda d1, d2: {**d1, **d2},
                (undot_key(key, value) for key, value in prefs.items()), )

            if useData:
                user_data_dir = parentFolder + "driver" + seperator + "chromeLog"
                options.add_argument(f"--user-data-dir={user_data_dir}")
                default_dir = os.path.join(user_data_dir, "Default")
                prefs_file = os.path.join(default_dir, "Preferences")
                with open(prefs_file, encoding="latin1", mode="w") as f:
                    json.dump(undot_prefs, f)
                del options._experimental_options["prefs"]


class wireChromeWithPrefs(seleniumWireWebdriver.Chrome):
    def __init__(self, *args, options=None,useData=True,**kwargs):
        if options:
            ChromeWithPrefs.handle_prefs(options,useData)
        super().__init__(*args, options=options,useData=useData, **kwargs)

        if useData:
            self.keep_user_data_dir = True
        else:
            self.keep_user_data_dir = False

def callUcDriver(useProxy=False, proxy=None, twoCaptcha=False, headless=False, useData=True,pageLoadStrategy='eager'):
    prefs = {'download.default_directory': parentFolder + "images" + seperator, 'intl.accept_languages': 'en,en_US'}
    caps = DesiredCapabilities().CHROME
    if useProxy and proxy != None:
        if type(proxy) != list:
            proxy = proxy.split(':')

        if len(proxy) > 2:
            IP = proxy[0]
            port = proxy[1]
            username = proxy[2]
            password = proxy[3]
            useAuth = True
        else:
            IP = proxy[0]
            port = proxy[1]
            useAuth = False

        if useAuth:
            wireOptions = {'proxy': {'http': 'http://' + username + ':' + password + '@' + IP + ':' + port,'https': 'https://' + username + ':' + password + '@' + IP + ':' + port,'no_proxy': 'localhost,127.0.0.1'}}
        else:
            wireOptions = {'proxy': {'http': 'http://@' + IP + ':' + port,'https': 'https://@' + IP + ':' + port,'no_proxy': 'localhost,127.0.0.1'}}

    caps["pageLoadStrategy"] = pageLoadStrategy
    op = webdriver.ChromeOptions()
    if headless:
        op.add_argument("--headless=new")

    # Sertifika hatasi alinmasi dahilinde,
    # python -m seleniumwire extractcert ile indirdiginiz
    # sertifikayi chrome'a ekleyiniz.

    op.add_argument('--ignore-certificate-errors')
    op.add_experimental_option("prefs", prefs)
    op.add_argument("--no-sandbox")
    op.add_argument("--dns-prefetch-disable")
    op.add_argument("--disable-gpu")
    op.add_argument("--disable-user-media-security=true")
    op.add_argument("--disable-popup-blocking")

    if twoCaptcha:
        op.add_argument('--load-extension={}HTML-Elements-Screenshot,{}2Captcha'.format(parentFolder + "extensions" + seperator, parentFolder + "extensions" + seperator))

    if useProxy:
        driver = wireChromeWithPrefs(options=op,driver_executable_path="chromedriver",desired_capabilities=caps, seleniumwire_options=wireOptions,useData=useData)
    else:
        driver = ChromeWithPrefs(options=op,driver_executable_path="chromedriver",desired_capabilities=caps,useData=useData)
    return driver

if __name__ == "__main__":
    proxyIP = input("Proxy IP: ")
    proxyPort = input("Proxy Port: ")
    proxyUsername = input("Proxy Username ( Leave it blank if doesn't have one ): ")
    proxyPassword = input("Proxy Password ( Leave it blank if doesn't have one ): ")
    if proxyUsername != '' and proxyPassword != '':
        proxy = [proxyIP,proxyPort,proxyUsername,proxyPassword]
    else:
        proxy = [proxyIP,proxyPort]
    driver = callUcDriver(True,proxy,useData=False)
    driver.get('https://www.google.com')
    print("Enjoy your stay.")
    while True:
        time.sleep(3600)