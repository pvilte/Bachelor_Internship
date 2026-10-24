from django.urls import path
from api.views import *

"""
URLs that specify the available API endpoints and link them to their views.
"""

urlpatterns = [
    # endpoint for collecting all traces:
    path('all-traces/', AllTraces.as_view(), name='all-traces'),

    # endpoint for collecting events with adaptations:
    path('events-with-adapt/', EventsWithAdapt.as_view(), name='events-with-adaptations'),

    # endpoint for collecting reason or impact of adaptation:
    path('reason-impact/<str:key>/', ReasonImpact.as_view(), name='reason-impact-of-adaptation'),

    # endpoint for collecting a single trace by its ID:
    path('trace-single-instance/<str:instance>/', SingleInstance.as_view(), name='single-instance'),

    # endpoint for collecting impact of instance:
    path('impact-of-instance/<str:instance>/', ImpactOfInstance.as_view(), name='impact-instance')

]