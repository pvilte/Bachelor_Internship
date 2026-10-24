from rest_framework.views import APIView
from rest_framework.response import Response

from retrieve.retrieve import *
from record.record import *
from prov_format import generate_prov

# Create your views here.
class AllTraces(APIView):
    """
    View to retrieve all traces in the database.
    """
    def get(self, request):
        """
        Return the list of all traces.
        """
        result = collect_all_traces()
        return Response(result)

class EventsWithAdapt(APIView):
    """
        View to retrieve all events with adaptations.
    """
    def get(self, request):
        """
        Return the list of all events with adaptations.
        """
        result = all_events_with_adaptations()
        return Response(result)

class ReasonImpact(APIView):
    """
    View to retrieve reason, impact or both keys of adaptations.
    """
    def get(self, request, key):
        """
        Return the list of either reson, impact or both keys of adaptations.
        """
        result = reason_and_impact_keys_of_adaptation(key)
        return Response(result)

class SingleInstance(APIView):
    """
        View to retrieve trace by the instance ID.
    """
    def get(self, request, instance):
        """
        Return the trace of an Instance.
        """
        result = collect_trace_based_on_trace_id(instance)
        return Response(result)

class ImpactOfInstance(APIView):
    """
        View to retrieve impact of an instance.
    """
    def get(self, request, instance):
        """
        Return the impact of instance:
        """
        result = collect_impact_of_instance(instance)
        return Response(result)