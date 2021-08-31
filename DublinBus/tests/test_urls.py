from django.test import SimpleTestCase
from django.urls import reverse, resolve
from Main.views import index, about, transport_details, settings, Historic, Model

class TestUrls(SimpleTestCase):

    def test_index(self):
        url = reverse('index')
        self.assertEquals(resolve(url).func, index)

    def test_Historic(self):
        url = reverse('Historic')
        self.assertEquals(resolve(url).func, Historic)
    
    def test_about(self):
        url = reverse('about')
        self.assertEquals(resolve(url).func, about)
    
    def test_transport_details(self):
        url = reverse('transport_details')
        self.assertEquals(resolve(url).func, transport_details)

    def test_settings(self):
        url = reverse('settings')
        self.assertEquals(resolve(url).func, settings)

    def test_Model(self):
        url = reverse('Model')
        self.assertEquals(resolve(url).func, Model)

    # def test_Traffic_Model(self):
    #     url = reverse('TrafficModel')
    #     self.assertEquals(resolve(url).func, TrafficModel)