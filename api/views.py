from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import HttpResponse

from retrieve.retrieve import *
from record.record import *
from prov_format.generate_prov import generate_prov

# Create your views here.
class AllTraces(APIView):
    """
    View to retrieve all traces in the database.
    """
    def get(self, request):
        """
        Return the list of all traces either in JSON or PROV-O.
        """
        retrieval_type = request.query_params.get("type", "default")

        result = collect_all_traces()

        if retrieval_type == "prov":
            # Return the RDF file containing generated PROV-O for the result:
            rdf_result = generate_prov("output")
            return HttpResponse(rdf_result.serialize(format="trig"), content_type="rdf")

        return Response(result)


class EventsWithAdapt(APIView):
    """
    View to retrieve all events with adaptations.
    """
    def get(self, request):
        """
        Return the list of all events with adaptations either in JSON or PROV-O.
        """
        retrieval_type = request.query_params.get("type", "default")

        result = all_events_with_adaptations()

        if retrieval_type == "prov":
            # Return the RDF file containing generated PROV-O for the result:
            rdf_result = generate_prov("output")
            return HttpResponse(rdf_result.serialize(format="trig"), content_type="rdf")
        
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
        Return the trace of an Instance either in JSON or PROV-O:
        """
        retrieval_type = request.query_params.get("type", "default")

        result = collect_trace_based_on_instance_id(instance)

        if retrieval_type == "prov":
            # Return the RDF file containing generated PROV-O for the result:
            rdf_result = generate_prov("output")
            return HttpResponse(rdf_result.serialize(format="trig"), content_type="rdf")
        
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


class TraceData(APIView):
    """
    View to record provenance data to database.
    """
    def post(self, request):
        """
        Record the JSON data to Neo4j database:
        """
        # take the JSON data inputted by user:
        data = request.data

        record_from_api(data)
        return Response("Recording complete!")


class ImpactData(APIView):
    """
    View to record overall impact of instance in database.
    """
    def put(self, request):
        """
        Record overall impact of instance in database:
        """
        # take the JSON data inputted by user:
        data = request.data
        
        record_impact_from_api(data)
        return Response("Recording complete!")
