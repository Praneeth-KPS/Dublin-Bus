from selenium import webdriver
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.urls import reverse
import time

class TestIndexPage(StaticLiveServerTestCase):

    def setUp(self):
        self.browser = webdriver.Chrome('functional_tests/chromedriver')

    def tearDown(self):
        self.browser.close()

    def test_get_map_is_displayed(self):
        self.browser.get(self.live_server_url)
        
        alert = self.browser.find_element_by_class_name('navbar-brand')
        self.assertEquals(
            alert.find_element_by_tag_name('h1').text,
            'Travel Hub'
        )

    def test_get_transport_details_click(self):
        self.browser.get(self.live_server_url)

        alert = self.browser.find_element_by_class_name('nav-item')
        alert1 = alert.find_element_by_tag_name('a').click()
        self.assertEquals(
            self.browser.current_url, 
            self.live_server_url+reverse('transport_details')
        )

    def test_get_about_click(self):
        self.browser.get(self.live_server_url)

        alert = self.browser.find_element_by_class_name('nav-item')
        alert1 = alert.find_element_by_id('about').click()
        self.assertEquals(
            self.browser.current_url, 
            self.live_server_url+reverse('about')
        )

    def test_get_settings_click(self):
        self.browser.get(self.live_server_url)

        alert = self.browser.find_element_by_class_name('nav-item')
        alert1 = alert.find_element_by_id('settings').click()
        self.assertEquals(
            self.browser.current_url, 
            self.live_server_url+reverse('settings')
        )