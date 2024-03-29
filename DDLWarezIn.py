#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re

from module.plugins.Crypter import Crypter

class DDLWarezIn(Crypter):
    __name__ = "DDLWarezIn"
    __type__ = "container"
    __pattern__ = r"http://[\w\.]*?ddl-warez\.in/download/.*?"
    __version__ = "0.1"
    __config__ = [("preferredHoster", "all;shareOnlineBiz;uploadedTo;cloudzerNet", "preferred hoster",
                   "ShareOnlineBiz")]
    __description__ = """ddl-warez.in Container Plugin"""
    __author_name__ = ("foo")
    __author_mail__ = ("foo@bar.de")

    def setup(self):
        self.multiDL = False

    def getHosts(self):
        item = self.getConfig("preferredHoster")
        if item == "all":
            return [1, 2, 3]
        elif item == "shareOnlineBiz":
            return [1]
        elif item == "uploadedTo":
            return [2]
        elif item == "cloudzerNet":
            return [3]
			
    def handleHost(self, html, host):

        if host == 1:
            match = re.search(r"\(share-online.biz\)", html)
        elif host == 2:
            match = re.search(r"\(uploaded.to\)", html)
        elif host == 3:
            match = re.search(r"\(cloudzer.net\)", html)

        match = re.search(r"download/links/(.*?)/(.*?) tar", html[match.start():])

        return str(match.group(0))[0:-5]

    def handleHostLinks(self, html, host):

        if host == 1:
            matches = re.findall(r"href=\"http://www.share-online.biz/dl/(.*?)\" tar", html)
            hostUrl = "http://www.share-online.biz/dl/"
        elif host == 2:
            matches = re.findall(r"href=\"http://ul.to/(.*?)\" tar", html)
            hostUrl = "http://ul.to/"
        elif host == 3:
            matches = re.findall(r"href=\"http://clz.to/(.*?)\" tar", html)
            hostUrl = "http://clz.to/"

        return [hostUrl + s for s in matches]
    
    def decrypt(self, pyfile):
        links = []

        hosts = self.getHosts()

        for host in hosts:

            html = self.req.load(self.pyfile.url, cookies=True)
            captchaHtmlUrl = "http://ddl-warez.in/"+self.handleHost(html, host)

            html = self.req.load(captchaHtmlUrl, cookies=True)
            match = re.search(r"captcha\.php\?id=(.*?)\" alt=\"\"", html)
            captchaUrl = "http://ddl-warez.in/captcha.php?id="+match.group(1)        
            result = self.decryptCaptcha(str(captchaUrl), imgtype="png")

            html = self.req.load(captchaHtmlUrl, cookies=True, post={"captcha":result, "sent":1})

            newLinks = self.handleHostLinks(html, host)

            links.extend(newLinks)

        self.packages.append((self.pyfile.package().name, links, self.pyfile.package().folder))