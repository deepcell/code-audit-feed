#!/usr/bin/python

import time, re, os
import synonymmapping
from common import *
re_gitsvn = re.compile('git-svn-id: \w+://.+ \w{4,12}-\w{4,12}-\w{4,12}-\w{4,12}-\w{4,12}')

class Commit:
    message = ''
    date = 0
    files = []
    def __init__(self, m, d, f):
        self.message = Commit.cleanUpCommitMessage(m)
        self.date = d
        self.files = f

        self.base_paths = self.getBasePath()
        self.keywords = self.getSynonyms()

    @staticmethod
    def cleanUpCommitMessage(msg):
        msg = re.sub(re_gitsvn, '', msg)
        return msg.strip()

    def getBasePath(self):
        if len(self.files) == 0: return ""
        trunks = [p for p in self.files if "/trunk" in p]
        branches = [p for p in self.files if "/branches" in p]
        tags = [p for p in self.files if "/tags" in p]
        odd = [p for p in self.files if p not in trunks and p not in branches and p not in tags]
        if ((1 if len(trunks) > 0 else 0) + (1 if len(branches) > 0 else 0) + \
                (1 if len(tags) > 0 else 0) + (1 if len(odd) > 0 else 0)) > 1:
                ret = []
                if len(trunks) > 0: ret.append(os.path.commonprefix(trunks))
                if len(branches) > 0: ret.append(os.path.commonprefix(branches))
                if len(tags) > 0: ret.append(os.path.commonprefix(tags))
                if len(odd) > 0: ret.append(os.path.commonprefix(odd))
                return ret
        else:
                return os.path.dirname(os.path.commonprefix(self.files))


    def getSynonyms(self):
        log = self.message.lower()
        paths = []
        for i in range(len(self.files)): paths.append(self.files[i].lower())

        keywords = set()
        for k in synonymmapping.map:
                if k in log:
                        keywords.add(k)
                        for v in synonymmapping.map[k]: keywords.add(v)
                for p in paths:
                        if k in p:
                                keywords.add(k)
                                for v in synonymmapping.map[k]: keywords.add(v)

        return keywords

        
    def pprint(self):
         print "Date:\t\t", unixToGitDateFormat(self.date), "(" + str(self.date) + ")"
         print "Log Message:\t", self.message
         if len(self.files) > 0:
             print "Files:\t\t", self.files[0]
             for p in self.files[1:]:
                 print "\t\t", p

         if len(self.base_paths) > 0:
             if len(self.base_paths) > 0 and not isinstance(self.base_paths, basestring):
                 print "Base Paths:\t", self.base_paths[0]
                 for p in self.base_paths[1:]:
                     print "\t\t", p
                 else:
                     print "Base Path:\t", self.base_paths
         print "Keywords:\t", ", ".join(self.keywords)
