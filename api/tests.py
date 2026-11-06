import unittest
from django.test import Client

# Create your tests here.
class APITests(unittest.TestCase):
    """
    Test class used for defining API GET functions.
    """

    def test_retrieving_all_traces(self):
        """
        Test used to evaluate whether the retrieval of all traces through the API
        was successful.
        """

        response = Client().get("/api/all-traces/")
        self.assertEqual(response.status_code, 200)
    

    def test_retrieving_single_trace(self):
        """
        Test used to evaluate whether the retrieval of a single trace through the API
        was successful.
        """

        response = Client().get('/api/trace-single-instance/Instance-95382/')
        self.assertEqual(response.status_code, 200)


    def test_retrieving_events_with_adaptations(self):
        """
        Test used to evaluate whether the retrieval of events with adaptatiopns through the API
        was successful.
        """

        response = Client().get('/api/events-with-adapt/')    
        self.assertEqual(response.status_code, 200)
        # the test data has two adaptations, thus, check if that was in the response:
        self.assertIn('E-Mail to request further information from client', response.content.decode('utf-8'))
        self.assertIn('Call to request further information from client', response.content.decode('utf-8'))


    def test_retrieving_reason_keys(self):
        """
        Test used to evaluate whether the retrieval of reason key of adaptation through the API
        was successful.
        """

        # test if reason keys are returned:
        response = Client().get('/api/reason-impact/reason/')       
        self.assertEqual(response.status_code, 200)
        # the test data has adaptation with the following reason, thus check if that reason was in the response:
        self.assertIn('Getting a faster response.', response.content.decode('utf-8'))


    def test_retrieving_reason_keys(self):
        """
        Test used to evaluate whether the retrieval of impact key of adaptation through the API
        was successful.
        """

        # test if reason keys are returned:
        response = Client().get('/api/reason-impact/impact/')       
        self.assertEqual(response.status_code, 200)
        # the test data has adaptation with the following impact, thus check if that reason was in the response:
        self.assertIn('Process speedup', response.content.decode('utf-8'))


    def test_retrieving_overall_impact(self):
        """
        Test used to evaluate whether the retrieval of overall impact through the API
        was successful.
        """

        response = Client().get('/api/impact-of-instance/Instance-95382/')  
        self.assertEqual(response.status_code, 200)
        # Test data contains only one overall impact, thus, check if it is in the response:
        self.assertIn('Process sped up', response.content.decode('utf-8'))
        
        
