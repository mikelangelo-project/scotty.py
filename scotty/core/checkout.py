import logging
import os

import git

logger = logging.getLogger(__name__)


# TODO use classmethods, since there is no state in the instance
class CheckoutManager(object):
    def checkout(self, git_url, workspace, git_ref=None):
        repo = self._get_repo(git_url, workspace)
        self._sync_repo(repo)
        self._checkout_ref(repo, git_ref)
        self._init_submodules(workspace, repo)

    def is_git_dir(self, path):
        return os.path.isdir('{path}/.git'.format(path=path))
        
    def _get_repo(self, git_url, workspace):
        if not self.is_git_dir(workspace.path):
            repo = git.Repo.clone_from(git_url, workspace.path)
        else:
            repo = git.Repo(workspace.path)
        return repo
            
    def _sync_repo(self, repo):
        repo.git.remote('update')
        repo.git.reset('--hard')
        repo.git.clean('-x', '-f', '-d', '-q')
        
    def _checkout_ref(self, repo, git_ref):
        if git_ref is not None:
            repo.remotes.origin.fetch(refspec=git_ref)
            repo.git.checkout('FETCH_HEAD')
            repo.git.reset('--hard', 'FETCH_HEAD')

    def _init_submodules(self, workspace, repo):
        if os.path.isfile('{path}/.gitmodules'.format(path=workspace.path)):
            repo.git.submodules('init')
            repo.git.submodules('sync')
            repo.git.submodules('update', '--init')
