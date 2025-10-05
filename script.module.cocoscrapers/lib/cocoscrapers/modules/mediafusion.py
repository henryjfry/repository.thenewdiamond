from cocoscrapers.modules import control
from cocoscrapers.modules import log_utils
from urllib.parse import urljoin
import requests
import time as time

getSetting = control.setting
session = requests.Session()

class MediaFusion:
    def __init__(self):
        if control.setting('mediafusion.usecustomurl') == 'true': 
            self.base_link = control.setting('mediafusion.customurl')
        else:
            self.base_link = 'https://mediafusion.elfhosted.com'
        if self.base_link == '':
            self.base_link = 'https://mediafusion.elfhosted.com'
        self.timeout = 20

    def auth(self):
        try:
            data = ''
            start = time.time()
            response = requests.post(urljoin(self.base_link, 'kodi/generate_setup_code'), json=data, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            code = data['code']
            
            expires_in = data['expires_in']
            verification_url = data.get('configure_url')
            user_code = ""
            line = '%s\n%s\n%s'
            progressDialog = control.progressDialog
            progressDialog.create("Mediafusion", control.progress_line % ("Open this link in a browser : %s" %  data.get('configure_url'), 'Kodi Code: %s' % code, ''))
            try:
                time_passed = 0
                while not progressDialog.iscanceled() and time_passed < expires_in:
                    try:
                        url = urljoin(self.base_link, f'kodi/get_manifest/{code}')
                        response = requests.get(url, timeout=20)
                        if response.status_code == 404:
                            time_passed = time.time() - start
                            progress = int(100)-int(100 * time_passed / expires_in)
                            progressDialog.update(progress, control.progress_line % ("Open this link in a browser : %s" %  data.get('configure_url'), 'Kodi Code: %s' % code, ''))
                            control.sleep(5*1000)
                    except requests.HTTPError as e:
                        log_utils.log('Request Error: %s' % str(e), __name__, log_utils.LOGDEBUG)
                        if e.response.status_code != 404: raise e
                        progress = int(100)-int(100 * time_passed / expires_in)
                        progressDialog.update(progress)
                        control.sleep(5*1000)
                    else:
                        if not response: continue
                        else: 
                            if response.status_code == 200:
                                data = response.json()
                                control.setSetting('mediafusion.userdata', data.get('secret_string'))
                                control.openSettings('1.24', 'script.module.cocoscrapers')
                                return control.notification(message="Successfully added custom MediaFusion url.")
            finally:
                progressDialog.close()
                control.openSettings('1.24', 'script.module.cocoscrapers')
            return None
        except:
            log_utils.error()

    def clear(self):
        control.setSetting('mediafusion.userdata', '')
        control.openSettings('1.24', 'script.module.cocoscrapers')
        return control.notification(message="Successfully cleared MediaFusion user data.")
        