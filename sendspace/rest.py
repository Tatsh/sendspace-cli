from io import StringIO
from os.path import getsize, realpath
from urllib.parse import urlencode
from urllib.request import urlopen, Request
import hashlib
import pycurl
import xml.etree.ElementTree as ET

API_ERROR_NO_METHOD = 1
API_ERROR_UNKNOWN_METHOD = 2
API_ERROR_SESSION_KEY_MISSING = 3
API_ERROR_PARAMETER_MISSING = 4
API_ERROR_BAD_API_VERSION = 5
API_ERROR_SESSION_BAD = 6
API_ERROR_SESSION_NOT_AUTH = 7
API_ERROR_AUTHENTICATION_FAILURE = 8
API_ERROR_FILE_NOT_FOUND = 9
API_ERROR_FOLDER_NOT_FOUND = 10
API_ERROR_PERMISSION_DENIED = 11
API_ERROR_DOWNLOAD_TEMP_ERROR = 12
API_ERROR_UPLOAD_TEMP_ERROR = 13
API_ERROR_FOLDER_NOT_EMPTY = 14
API_ERROR_SYSTEM_MAINTENANCE = 15
API_ERROR_INVALID_PARAMETER = 16
API_ERROR_HTTPS_FORBIDDEN = 17
API_ERROR_UNKNOWN_API_KEY = 18
API_ERROR_PRO_EXPIRED = 19
API_ERROR_PRO_DISKSPACE_LIMIT = 20
API_ERROR_PARAMETER_BAD_VALUE = 21
API_ERROR_BAD_PASSWORD = 22
API_ERROR_BANDWIDTH_LIMIT = 23
API_ERROR_INVALID_EMAIL = 24
API_ERROR_OUTDATED_VERSION = 25
API_ERROR_INVALID_FILE_URL = 26
API_ERROR_REGISTRATION_ERROR = 27
API_ERROR_CONTACT_EXISTS = 28
API_ERROR_CONTACT_NOT_EXISTS = 29
API_ERROR_TOO_MANY_SESSIONS = 30
API_ERROR_BAD_TARGET_FOLDER = 31
API_ERROR_CONTACTS_LIMIT = 32
API_ERROR_FOLDER_IS_PRIVATE = 33

CHROME_USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1700.14 Safari/537.36'

class SendspaceRESTAPIError(Exception):
    pass

class SendspaceRESTAPI:
    API_VERSION = '1.0'
    APP_VERSION = '0.1'
    API_URL = 'http://api.sendspace.com/rest/'

    _api_key = None
    _session_key = None

    def __init__(self, api_key):
        self._api_key = api_key

        if not self._api_key:
            raise Exception('Cannot use empty API key')

    def login(self, username, password):
        params = [
            ('api_key', self._api_key),
            ('api_version', self.API_VERSION),
            ('response_format', 'xml'),
            ('app_version', self.APP_VERSION),
        ]

        response = self._call_api_method('auth.createtoken', params)
        token = response['params']['token'][0]['value']

        password_md5 = hashlib.md5()
        password_md5.update(password.encode('utf-8'))
        password_md5 = password_md5.hexdigest()
        tokened_password = hashlib.md5()
        tokened_password.update((token + password_md5).encode('utf-8'))
        tokened_password = tokened_password.hexdigest()

        params = [
            ('token', token),
            ('user_name', username),
            ('tokened_password', tokened_password),
        ]

        response = self._call_api_method('auth.login', params)

        if not response:
            raise SendspaceRESTAPIError('Unable to login. Verify credentials')

        self._session_key = response['params']['session_key'][0]['value']

        return self._session_key

    def check_session(self):
        self._call_api_method('auth.checksession', [
            ('session_key', self._session_key),
        ])

    def set_session_id(self, session_key):
        self._session_key = session_key
        self.check_session()

    def logout(self):
        if not self._session_key:
            raise SendspaceRESTAPIError('Not logged in')

        params = [
            ('session_key', self._session_key),
        ]
        response = self._call_api_method('auth.logout', params)

        if not response:
            raise SendspaceRESTAPIError('Could not log out (probably ignorable)')

    def get_upload_info(self, speed_limit=0, **kwargs):
        if not self._session_key:
            raise SendspaceRESTAPIError('Not logged in')

        valid_keys = [
            'description',
            'password',
            'folder_id',
            'recipient_email',
            'notify_uploader',
            'redirect_url',
        ]
        params = [
            ('session_key', self._session_key),
            ('speed_limit', 0),
        ]

        for key, value in kwargs.items():
            if key not in valid_keys:
                raise SendspaceRESTAPIError('Invalid argument: %s' % (key))

            if value:
                params.append((key, value,))

        return self._call_api_method('upload.getinfo', params)

    # TODO Give more detailed structured output
    # TODO Pass description, recipient_email, notify_uploader arguments
    def upload_file(self, filename, speed_limit=0, target=None, user_agent=CHROME_USER_AGENT, **kwargs):
        info = self.get_upload_info(speed_limit=0, **kwargs)
        post_url = info['params']['upload'][0]['attributes']['url']
        progress_url = info['params']['upload'][0]['attributes']['progress_url']
        identifier = info['params']['upload'][0]['attributes']['upload_identifier']
        max_filesize = int(info['params']['upload'][0]['attributes']['max_file_size'])
        extra_info = info['params']['upload'][0]['attributes']['extra_info']
        filename = realpath(filename)

        if getsize(filename) > max_filesize:
            print('%s size is greater than max file size of %d bytes' % (filename, max_filesize))

        try:
            with open(filename, 'rb') as f:
                params = [
                    ('MAX_FILE_SIZE', str(max_filesize)),
                    ('UPLOAD_IDENTIFIER', identifier),
                    ('extra_info', extra_info),
                    ('userfile', (pycurl.FORM_FILE, filename,)),
                    #'description': '',
                    #'recipient_email': '',
                    #'notify_uploader': '',
                ]

                c = pycurl.Curl()

                c.setopt(c.URL, post_url)
                c.setopt(c.HTTPPOST, params)
                c.setopt(c.USERAGENT, user_agent)
                #c.setopt(c.VERBOSE, True)

                b = StringIO()
                c.setopt(pycurl.WRITEFUNCTION, b.write)
                c.perform()
                c.close()

                content = b.getvalue()
                file_id = None

                if 'upload_status=fail' in content:
                    raise SendspaceRESTAPIError('Could not upload file: %s' % (content))

                for line in content.splitlines():
                    if 'file_id=' in line:
                        file_id = line.split('=')[1]
                        break

                if not file_id:
                    raise SendspaceRESTAPIError('Could not upload file: file ID not found')

                return {
                    'url': 'http://www.sendspace.com/file/%s' % (file_id)
                }
        except IOError:
            raise SendspaceRESTAPIError('File %s could not be opened' % (filename))


    def _parse_response(self, xml):
        root = ET.fromstring(xml)
        ret = {
            'params': {},
        }

        if root.tag != 'result':
            return None

        ret['result'] = root.attrib

        for child in root:
            tag_val = {
                'value': child.text,
                'attributes': child.attrib,
            }

            try:
                ret['params'][child.tag].append(tag_val)
            except KeyError:
                ret['params'][child.tag] = [tag_val]

        if len(ret.items()) == 0:
            return None

        return ret

    def _call_api_method(self, method, params=[]):
        url = self.API_URL
        params = urlencode(params)
        url += '?method=%s&%s' % (method, params)

        response = urlopen(url)
        contents = response.read().decode('utf-8')

        if not contents:
            raise SendspaceRESTAPIError('Nothing returned for method %s' % (method))

        response = self._parse_response(contents)

        if response['result']['method'] != method:
            raise SendspaceRESTAPIError('Unexpected API client error (method received is not the same as method sent)')

        if response['result']['status'] != 'ok':
            raise SendspaceRESTAPIError('Status not "ok", error: %s' % (response['params']['error'][0]['attributes']['text'],))

        return response
