#!/usr/bin/env python
"""A smoke test for containers"""

import json
import logging
import os
import pytest
import requests
import time

from kubetest_stdlib import testutils
from requests.packages.urllib3.exceptions import InsecureRequestWarning

# Supress warnings
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

logger = logging.getLogger(__name__)


class TestSmoke():
    """ Use pytest to execute rest api operations against a container. """

    @classmethod
    def setup_class(cls):
        """
        Setup environment for the upcoming tests. This is basically the constructor for
        this test class. Its used to create the KubeUtils API instance used by some
        tests, retrieve environment variables from the testconfig.yaml and set up any
        structures and variables that might be used by All of the test methods below.

        """
        # Initial setup
        test_target = "esp"
        test_vars = testutils.k8s_test_setup(test_target)
        # Expose variables to test functions
        cls.TARGET_BASE_NAME = test_target
        cls.TARGET_POD_NAME  = test_vars.get("target_pod_name")
        cls.NAMESPACE        = test_vars.get("namespace")
        cls.kubeutilobj      = test_vars.get("kubeutilobj")


    def test_01_pod_user_not_root(self):
        """
        Check user not root
        """
        time.sleep(1)
        cmd = "exec {} whoami".format(self.TARGET_POD_NAME)
        status,result = self.kubeutilobj.kubectl(cmd, self.NAMESPACE)
        error_flag = False
        if "failure" in status.lower() or b"root" in result["output"]:
            error_flag = True
        assert error_flag == False

    def test_02_espserver_hostname(self):
        """
        Check consul in hostname
        """
        cmd = "exec {} hostname".format(self.TARGET_POD_NAME)
        status, result = self.kubeutilobj.kubectl(cmd, self.NAMESPACE)
        assert self.TARGET_BASE_NAME in result["output"].decode("utf-8")

    def test_03_espserver_http(self):
        """
        Check the http endpoint for esp
        """
        url = "http://localhost:31415/SASESP"
        cmd = 'exec {} -- curl -s '.format(self.TARGET_POD_NAME) + ' {}'.format(url)
        status, result = self.kubeutilobj.kubectl(cmd, self.NAMESPACE)
        logger.debug(result['output'])
        assert b"200" in result["output"]
