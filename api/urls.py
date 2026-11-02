from django.urls import path
from api.views import *
from drf_yasg.views import get_schema_view 
from drf_yasg import openapi

"""
URLs that specify the available API endpoints and link them to their views.
"""

# Creates the Swagger documentation for testing the API endpoints:
schema_view = get_schema_view(
    openapi.Info(
        title="Provenance API",
        default_version='v1',
    ),
    public=True,
)

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
    path('trace/impact/', ImpactData.as_view(), name='record-impact-of-trace'),

    # endpoint that displays the swagger documentation for all possible endpoints:
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='swagger')

]