import argparse
from record.record import *
from retrieve.retrieve import *
from prov_format.generate_prov import *

def main():
    """
    This function parses command-line arguments and runs selected functions:
    either record, retrieve, or prov.

    Commands available:
    - record: calls record() from record/record.py
    - retrieve: calls selected function from retrieve/retrieve.py
    - prov: calls generate_prov() from prov_format/generate_prov.py

    """

    parser = argparse.ArgumentParser(
        prog='Record/Retrieve/Generate PROV-O',
        description='Record, Retrieve, and generate PROV-O format for event provenance'
    )

    # add subparsers for retrieve and record functions:
    subparsers = parser.add_subparsers(help='choose either retrieve, record or prov_format', dest='chosen', required=True)
    subparsers.add_parser('record', help='Record event data to graph database')
    retrieve_parser = subparsers.add_parser('retrieve', help='Retrieve selected event data from database')
    # create a prov argument for retrieve to run generate_prov() function on results:
    retrieve_parser.add_argument('--prov', action='store_true', help='Return retrieval result in PROV-O format')


    # create different commands for different retrieve cases:
    retrieve_commmands = retrieve_parser.add_subparsers(dest='selected_case', required=True)


    # 1. Retrieve all:
    retrieve_commmands.add_parser('all', help='Retrieve all contents from the database').set_defaults(case_nr=1)


    # 2. Retrieve direct neighbours:
    direct_neighbours = retrieve_commmands.add_parser('direct_neighbours_collect', help='Retrieve all direct neighbours collected on a label')
    direct_neighbours.add_argument('node1', type=str,  help='First node')
    direct_neighbours.add_argument('node2', type=str,  help='Second node on which collect will be performed')
    direct_neighbours.set_defaults(case_nr=2)


    #  create count commands for different retrieve count cases:
    count = retrieve_commmands.add_parser('count', help='Retrieve data using a count function')
    count_commands = count.add_subparsers(dest='count_case', required=True)
    

    # 3. Retrieve count of all nodes in database:
    count_commands.add_parser('all', help="Retrieve count of all nodes in database").set_defaults(case_nr=3)

    # 4. Retrieve count of direct neighbours of a node
    direct_neighbours_count = count_commands.add_parser('direct_neighbours', help="Retrieve count of nodes direct neighbours")
    direct_neighbours_count.add_argument('node1', type=str, help='First node')
    direct_neighbours_count.add_argument('node2', type=str,  help='Second node whose labels will be counted')
    direct_neighbours_count.set_defaults(case_nr=4)

    # 5. Retrieve count of all nodes of given label:
    nodes_label_count = count_commands.add_parser('node_label', help="Retrieve count of nodes with given label")
    nodes_label_count.add_argument('label',  help='label of node we want to count')
    nodes_label_count.set_defaults(case_nr=5)

    # 6. Retrieve count of nodes based on property value:
    count_nodes_property = count_commands.add_parser('nodes_property', help="Retrieve count of nodes with specified property values")
    count_nodes_property.add_argument('label', type=str, help='Label of node')
    count_nodes_property.add_argument('property', type=str,  help='Property of node')
    count_nodes_property.add_argument('value', type=str,  help='Value of the property')
    count_nodes_property.set_defaults(case_nr=6)

    # 7. Retrieve count of all relationships in database:
    count_commands.add_parser('all_relationships', help="Retrieve count of all relationships in database").set_defaults(case_nr=7)
    

    # 8. Retrieve nodes based on label and property value:
    nodes_label_property = retrieve_commmands.add_parser('nodes_label_property', help='Retrieve all nodes based on label and property value')
    nodes_label_property.add_argument('label', type=str, help='Label of node')
    nodes_label_property.add_argument('property', type=str, help='Property of node')
    nodes_label_property.add_argument('value', type=str, help='Value of the property')
    nodes_label_property.set_defaults(case_nr=8)


    # 9. Retrieve relationship between two nodes:
    node_relationship = retrieve_commmands.add_parser('node_relationship', help="Retrieve relationship between two nodes")
    node_relationship.add_argument('node1', type=str, help='First node')
    node_relationship.add_argument('node2', type=str, help='Second node')
    node_relationship.set_defaults(case_nr=9)


    # 10. Retrieve property keys based on node label:
    node_properties = retrieve_commmands.add_parser('node_properties', help='Retrieve node properties based on label')
    node_properties.add_argument('label', type=str, help='Label of node')
    node_properties.set_defaults(case_nr=10)


    # 11. Retrieve all labels in database:
    retrieve_commmands.add_parser('all_labels', help="Retrieve all labels in database").set_defaults(case_nr=11)


    # 12. Retrieve all relationships in database:
    retrieve_commmands.add_parser('all_relationships', help="Retrieve all relationships in database").set_defaults(case_nr=12)


    # 13. Retrieve all disconnected nodes in database:
    retrieve_commmands.add_parser('disconnected_nodes', help="Retrieve all disconnected nodes in database").set_defaults(case_nr=13)


    # 14. Retrieve node of most incomming relationships based on label:
    most_incoming_rel = retrieve_commmands.add_parser('most_incomming_rel', help="Retrieve node of most incomming relationships based on label")
    most_incoming_rel.add_argument('label', type=str, help='Label of node')
    most_incoming_rel.set_defaults(case_nr=14)


    # 15. Retrieve all events with adaptations:
    retrieve_commmands.add_parser('events_with_adapt', help="Retrieve all events with adaptations in database").set_defaults(case_nr=15)


    # 16. Retrieve reason and impact keys of an adaptation:
    reason_impact = retrieve_commmands.add_parser('reason_impact', help="Retrieve reason, impact, or both of event adaptation")
    reason_impact.add_argument('key', type=str, help='Impact, reason, or both of adaptations')
    reason_impact.set_defaults(case_nr=16)


    # 17. Retrieve trace based on instance_id:
    trace_single_instance = retrieve_commmands.add_parser('trace_single_instance', help='Retreieve trace based on instance_id')
    trace_single_instance.add_argument('instance_id', type=str, help='Instance ID of the trace we want')
    trace_single_instance.set_defaults(case_nr=17)


    # 18. Retrieve all traces:
    retrieve_commmands.add_parser('all_traces', help='Retreieve all traces from database').set_defaults(case_nr=18)


    # 19. Retrieve impact of instance:
    impact_instance = retrieve_commmands.add_parser('impact_of_instance', help='Retreieve overall impact of instance')
    impact_instance.add_argument('instance_id', type=str,  help='Instance ID whose impact we want')
    impact_instance.set_defaults(case_nr=19)


    # Collect the arguments from the CLI
    args = parser.parse_args()


    # depending on selected command, run the function:
    if args.chosen == 'record':
        record("json_files")
        print("Record complete!\n")
    elif args.chosen == 'retrieve':
        match args.case_nr:
            case 1:
                retrieve_all()
            case 2:
                direct_neighbors_collect(args.node1, args.node2)
            case 3:
                count_all_nodes()
            case 4:
                count_direct_neighbors(args.node1, args.node2)
            case 5:
                count_nodes_label(args.label)
            case 6:
                count_based_on_property_value(args.label, args.property, args.value)
            case 7:
                count_all_relationships()
            case 8:
                nodes_property_value(args.label, args.property, args.value)
            case 9:
                two_node_relationships(args.node1, args.node2)
            case 10:
                property_keys(args.label)
            case 11:
                all_labels()
            case 12:
                all_relationships()
            case 13:
                disconnected_nodes()
            case 14:
                most_incoming_relationships_to_nodes(args.label)
            case 15:
                result = all_events_with_adaptations()
            case 16:
                result = reason_and_impact_keys_of_adaptation(args.key)
            case 17:
                result = collect_trace_based_on_trace_id(args.instance_id)
            case 18:
                result = collect_all_traces()
            case 19:
                result = collect_impact_of_instance(args.instance_id)
        print("Retrieval complete!\n")

        # If generating prov was selected, check if it can be created for the case:
        allowed_cases = {15, 17, 18}
        
        if args.prov and (args.case_nr in allowed_cases):
            result = generate_prov("output")
            print("Generated a PROV-O document\n")
        elif args.prov and (args.case_nr not in allowed_cases):
            raise Exception("PROV-O cannot be generated for this retrieved case")

if __name__ == "__main__":
    main()