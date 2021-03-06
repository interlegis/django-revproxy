
from mock import patch

import os

from django.test import TestCase, RequestFactory

from revproxy.views import ProxyView, DiazoProxyView

from .utils import get_urlopen_mock


class ViewTest(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        urlopen_mock = get_urlopen_mock()
        self.urlopen_patcher = patch('urllib3.PoolManager.urlopen',
                                     urlopen_mock)
        self.urlopen = self.urlopen_patcher.start()

    def test_upstream_not_implemented(self):
        proxy_view = ProxyView()
        with self.assertRaises(NotImplementedError):
            upstream = proxy_view.upstream

    def test_upstream_overriden(self):
        class CustomProxyView(ProxyView):
            upstream = 'http://www.google.com/'

        proxy_view = CustomProxyView()
        self.assertEqual(proxy_view.upstream, 'http://www.google.com/')

    def test_default_diazo_rules(self):
        class CustomProxyView(DiazoProxyView):
            pass

        proxy_view = CustomProxyView()

        correct_path = os.path.join(os.path.dirname(__file__), 'diazo.xml')
        self.assertEqual(proxy_view.diazo_rules, correct_path)

    def test_diazo_rules_overriden(self):
        class CustomProxyView(DiazoProxyView):
            diazo_rules = '/tmp/diazo.xml'

        proxy_view = CustomProxyView()
        self.assertEqual(proxy_view.diazo_rules, '/tmp/diazo.xml')

    def test_default_diazo_theme_template(self):
        proxy_view = DiazoProxyView()
        self.assertEqual(proxy_view.diazo_theme_template, 'diazo.html')

    def test_default_html_attr(self):
        proxy_view = DiazoProxyView()
        self.assertFalse(proxy_view.html5)

    def test_default_add_remote_user_attr(self):
        proxy_view = DiazoProxyView()
        self.assertFalse(proxy_view.add_remote_user)

    def test_tilde_is_not_escaped(self):
        class CustomProxyView(ProxyView):
            upstream = 'http://example.com'

        request = self.factory.get('/~')
        CustomProxyView.as_view()(request, '/~')

        url = 'http://example.com/~'
        headers = {u'Cookie': u''}
        self.urlopen.assert_called_with('GET', url,
                                        body=b'',
                                        redirect=False,
                                        retries=None,
                                        preload_content=False,
                                        decode_content=False,
                                        headers=headers)

    def test_space_is_escaped(self):
        class CustomProxyView(ProxyView):
            upstream = 'http://example.com'

        path = '/ test test'
        request = self.factory.get(path)
        CustomProxyView.as_view()(request, path)

        url = 'http://example.com/+test+test'
        headers = {u'Cookie': u''}
        self.urlopen.assert_called_with('GET', url,
                                        body=b'',
                                        redirect=False,
                                        retries=None,
                                        preload_content=False,
                                        decode_content=False,
                                        headers=headers)
