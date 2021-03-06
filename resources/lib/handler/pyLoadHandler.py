# -*- coding: utf-8 -*-
from resources.lib.config import cConfig
from resources.lib.gui.gui import cGui
from resources.lib.tools import logger
from string import maketrans
import sys
try:
    from urllib2 import Request, urlopen, build_opener, HTTPError
    from urllib import urlencode, quote_plus
except ImportError:
    from urllib.request import Request, urlopen, build_opener
    from urllib.error import HTTPError
    from urllib.parse import urlencode, quote_plus


class cPyLoadHandler:
    def __init__(self):
        self.config = cConfig()

    def sendToPyLoad(self, sPackage, sUrl):
        logger.info('PyLoad package: ' + str(sPackage) + ', ' + str(sUrl))
        if self.__sendLinkToCore(sPackage, sUrl):
            cGui().showInfo('PyLoad', 'Link gesendet', 5)
        else:
            cGui().showInfo('PyLoad', 'Fehler beim Senden des Links!', 5)

    def __sendLinkToCore(self, sPackage, sUrl):
        logger.info('Sending link...')
        try:
            py_host = self.config.getSetting('pyload_host')
            py_port = self.config.getSetting('pyload_port')
            py_user = self.config.getSetting('pyload_user')
            py_passwd = self.config.getSetting('pyload_passwd')
            mydata = [('username', py_user), ('password', py_passwd)]
            mydata = urlencode(mydata)
            # check if host has a leading http://
            if (py_host.find('http://') != 0):
                py_host = 'http://' + py_host
            logger.info('Attemting to connect to PyLoad at: ' + py_host + ':' + py_port)
            req = Request(py_host + ':' + py_port + '/api/login', mydata)
            req.add_header("Content-type", "application/x-www-form-urlencoded")
            page = urlopen(req).read()
            page = page[1:]
            session = page[:-1]
            opener = build_opener()
            opener.addheaders.append(('Cookie', 'beaker.session.id=' + session))
            # pyLoad doesn't like utf-8, so converting Package name to ascii, also stripping any characters that do not belong into a path name (\/:*?"<>|)
            sPackage = str(sPackage).decode("utf-8").encode('ascii', 'replace').translate(maketrans('\\/:*?"<>|', '_________'))
            py_url = py_host + ':' + py_port + '/api/addPackage?name="' + quote_plus(sPackage) + '"&links=["' + quote_plus(sUrl) + '"]'
            logger.info('PyLoad API call: ' + py_url)
            sock = opener.open(py_url)
            sock = sock.read()
            sock.close()
            return True
        except HTTPError as e:
            logger.info('unable to send link: Error= ' + str(sys.exc_info()[0]))
            logger.info(e.code)
            logger.info(e.read())
            try:
                sock.close()
            except:
                logger.info('unable to close socket...')
            return False
