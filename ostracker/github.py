''' rudimentary github API client for django-ostracker '''

import json
import urllib

def _result_to_obj(cls, result):
    if isinstance(result, dict):
        return cls(result)
    else:
        return [cls(o) for o in result]

class ApiObject(object):
    def __init__(self, d):
        self.__dict__.update(d)

    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, self.__dict__)

class Repository(ApiObject):
    pass

class Commit(ApiObject):
    pass

class Issue(ApiObject):
    pass

class GithubApiError(Exception):
    pass

class Endpoint(object):

    def _apicall(self, method, params=None, post=False):
        if self._credentials:
            params = urllib.urlencode(self._credentials)
        else:
            params = ''
        url = 'http://github.com/api/v2/json/%s?%s' % (method, params)
        response = urllib.urlopen(url).read()
        jsonresp = json.loads(response)
        if 'error' in jsonresp:
            raise GithubApiError(jsonresp['error'][0]['error'])
        return jsonresp

    def __init__(self, credentials):
        self._credentials = credentials

class RepositoryEndpoint(Endpoint):
    def search(self, q):
        resp = self._apicall('repos/search/%s' % q)
        return _result_to_obj(Repository, resp['repositories'])

    def get(self, owner, name):
        resp = self._apicall('repos/show/%s/%s' % (owner, name))
        return _result_to_obj(Repository, resp['repository'])

    def for_user(self, user):
        resp = self._apicall('repos/show/%s' % user)
        return _result_to_obj(Repository, resp['repositories'])

    # watch / unwatch
    # fork / create / delete
    # set_public / set_private
    # keys / add_key / remove_key
    # add/remove collaborators

    def get_collaborators(self, owner, name):
        resp = self._apicall('repos/show/%s/%s/collaborators' % (owner, name))
        return resp['collaborators']

    def get_network(self, owner, name):
        resp = self._apicall('repos/show/%s/%s/network' % (owner, name))
        return _result_to_obj(Repository, resp['network'])

    def get_languages(self, owner, name):
        resp = self._apicall('repos/show/%s/%s/languages' % (owner, name))
        return resp['languages']

    def get_tags(self, owner, name):
        resp = self._apicall('repos/show/%s/%s/tags' % (owner, name))
        return resp['tags']

    def get_branches(self, owner, name):
        resp = self._apicall('repos/show/%s/%s/branches' % (owner, name))
        return resp['branches']

class CommitEndpoint(Endpoint):
    def get_commits(self, owner, name, branch='master', path=''):
        if path:
            path = '/'+path
        resp = self._apicall('commits/list/%s/%s/%s%s' % (owner, name, branch,
                                                          path))
        return _result_to_obj(Commit, resp['commits'])

    def get_commit(self, owner, name, sha):
        resp = self._apicall('commits/show/%s/%s/%s' % (owner, name, sha))
        return _result_to_obj(Commit, resp['commit'])

class IssueEndpoint(Endpoint):
    def get_issues(self, owner, name, open=True, search=None):
        state = 'open' if open else 'closed'
        if search:
            url = 'issues/search/%s/%s/%s/%s' % (owner, name, state, search)
        else:
            url = 'issues/list/%s/%s/%s' % (owner, name, state)
        resp = self._apicall(url)
        return _result_to_obj(Issue, resp['issues'])

    def get_issue(self, owner, name, number):
        resp = self._apicall('/issues/show/%s/%s/%s' % (owner, name, number))
        return _result_to_obj(Issue, resp['issue'])

    # open / edit / close / reopen
    # labels
    # comment

# User API
    # user_search
    # get_user (update?)
    # follower mgmt
    # key mgmt
    # email mgmt
    # watched repos

# object API
# network API

class Github(object):
    def __init__(self, login=None, token=None):
        if login and token:
            credentials = {'login': login, 'token': token}
        else:
            credentials = None
        self.repos = RepositoryEndpoint(credentials)
        self.commits = CommitEndpoint(credentials)
        self.issues = IssueEndpoint(credentials)

