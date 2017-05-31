import unittest
import os

import mock

from scotty.core.checkout import CheckoutManager
from scotty.core.workspace import ExperimentWorkspace
from scotty.core.exceptions import ScottyException


class CheckoutManagerTest(unittest.TestCase):
    @mock.patch('git.cmd')
    def test_checkout(self, git_mock):
        workspace = ExperimentWorkspace('samples/components/experiment')
        checkout_manager = CheckoutManager()
        checkout_manager.checkout(
            workspace=workspace,
            project='project',
            origin_url='origin_url',
            update_url=None,
            ref='ref')
        unpacked_calls = self._unpack_calls(git_mock.mock_calls)
        expected_calls = [('Git', (os.path.abspath('samples/components/experiment'),), {}),
                          ('Git().clone', ('origin_urlproject', '.'), {}),
                          ('Git().remote', ('update',), {}),
                          ('Git().reset', ('--hard',), {}),
                          ('Git().clean', ('-x', '-f', '-d', '-q'), {}),
                          ('Git().fetch', ('origin_urlproject', 'ref'), {}),
                          ('Git().checkout', ('FETCH_HEAD',), {}),
                          ('Git().reset', ('--hard', 'FETCH_HEAD'), {}),
                          ('Git().clean', ('-x', '-f', '-d', '-q'), {})]
        self.assertEquals(unpacked_calls, expected_calls)

    def _unpack_calls(self, mock_calls):
        unpacked_calls = []
        for mock_call in mock_calls:
            name, args, kwargs = mock_call
            unpacked_calls.append((name, args, kwargs))
        return unpacked_calls

    def test_refs_tags(self):
        checkout_manager = CheckoutManager()
        with self.assertRaises(ScottyException):
            checkout_manager._update_repo(repo=None, url=None, ref='refs/tags')

    @mock.patch('os.path.isfile', return_value=True)
    def test_submodules(self, isfile_mock):
        repo_mock = mock.MagicMock()
        repo_mock.submodules.return_value = None
        workspace_mock = mock.MagicMock()
        workspace_mock.path.return_value = ''
        checkout_manager = CheckoutManager()
        checkout_manager._init_submodules(workspace=workspace_mock, repo=repo_mock)
        workspace_mock.path.__str__.assert_called_once()
        unpacked_calls = self._unpack_calls(repo_mock.mock_calls)
        expected_calls = [('submodules', ('init',), {}),
                          ('submodules', ('sync',), {}),
                          ('submodules', ('update', '--init'), {})]
        self.assertEquals(unpacked_calls, expected_calls)
