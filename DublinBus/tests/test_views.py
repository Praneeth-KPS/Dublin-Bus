from logging import setLogRecordFactory
from django.http import response
from django.test import TestCase, Client, client
from django.urls import reverse
import json

class TestViews(TestCase):
    def test_views_index(self):
        client = Client()
        response = client.get(reverse('index'))
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'index.html')

    def test_views_about(self):
        client = Client()
        response = client.get(reverse('about'))
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'about.html')
    
    def test_views_transport_details(self):
        client = Client()
        response = client.get(reverse('transport_details'))
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'transport_details.html')

    def test_views_settings(self):
        client = Client()
        response = client.get(reverse('settings'))
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'settings.html')


    # def test_views_primary_model(self):
    #     client = Client()
    #     response = self.client.get(reverse('Model' , json.dumps('Details')))
    #     # [[{'BusNumber': '13', 'Distance': '14', 'DepCoord': {'lat': '54.2719', 'lng': '-6.3189'}, 'ArrCord': {'lat': '53.0127', 'lng': '-6.5921'}, 'TotalBusStops': '15', 'Est_journey_time': '7500', 'Dept_time_24_hr': '16', 'Day_Of_Week': '1', 'Month': 'Aug', 'Rush_hr': '1', 'Date': '19 Aug 2021'}]]
    #     # , args=['Details']))
    #     # ,  **{'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'})
        
    #     self.assertEqual(response.status_code, 200)
    #     self.assertEquals(response, json)
        
       