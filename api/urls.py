from django.urls import path
from api.views import *

"""
URLs that specify the available API endpoints and link them to their views.
"""

urlpatterns = [
    # endpoint to display all traces:
    path('all-traces/', AllTraces.as_view(), name='all-traces'),

    # endpoint to display events with adaptations:
    path('events-with-adapt/', EventsWithAdapt.as_view(), name='events-with-adaptations'),

    # endpoint to display reason or impact of adaptation:
    path('reason-impact/<str:key>/', ReasonImpact.as_view(), name='reason-impact-of-adaptation'),

    # endpoint to display a single trace by its ID:
    path('trace-single-instance/<str:instance>/', SingleInstance.as_view(), name='single-instance'),

    # endpoint to display impact of instance:
    path('impact-of-instance/<str:instance>/', ImpactOfInstance.as_view(), name='impact-instance'),

    # endpoint that accepts new traces that are then added to database:
    path('traces/', TraceData.as_view(), name='record-traces-to-database'),

    # endpoint that accepts a trace's overall impact(s) which is then added to the database:
    path('trace/impact/', ImpactData.as_view(), name='record-impact-of-trace')

]