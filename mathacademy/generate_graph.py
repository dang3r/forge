#!/usr/bin/env python3
import json
from graphviz import Digraph


def load_topics(filepath):
    """
    Loads the topics from the JSON file. This file is expected to have a top-level "topics"
    key, which holds a dictionary of topic objects.
    """
    with open(filepath, "r") as f:
        data = json.load(f)
    if isinstance(data, dict) and "topics" in data:
        return data["topics"]
    return data


def group_topics_by_course_and_unit(topics):
    """
    Groups topics by course and then by unit.

    Returns:
      grouped: A dict keyed by (course_id, course_name) with values as dicts that are keyed
               by (unit_id, unit_name). The innermost value is a list of topic objects.
      lessons: A flat dictionary mapping each topic id to its topic object (for looking up prerequisites).
    """
    grouped = {}
    lessons = {}
    for _, topic in topics.items():
        lessons[topic["id"]] = topic
        course_info = topic.get("course", {})
        course_id = course_info.get("id", "NoCourse")
        course_name = course_info.get("name", "No Course")
        unit_info = topic.get("unit", {})
        unit_id = unit_info.get("id", "NoUnit")
        unit_name = unit_info.get("name", "No Unit")
        course_key = (course_id, course_name)
        unit_key = (unit_id, unit_name)
        if course_key not in grouped:
            grouped[course_key] = {}
        if unit_key not in grouped[course_key]:
            grouped[course_key][unit_key] = []
        grouped[course_key][unit_key].append(topic)
    return grouped, lessons


def create_graph(grouped, lessons):
    """
    Creates a Graphviz Digraph that visualizes the topics.

    - Creates a top-level graph with left-to-right layout.
    - For each course, a subgraph (cluster) is created and given a light blue color.
    - Within each course, each unit is clustered (with a light yellow fill).
    - Each lesson (topic) node is given a unique name built from its id.
      It is colored "lightgreen" if its repetition value is nonzero (i.e. the lesson is done)
      and "lightgrey" otherwise.
    - Edges are drawn from each prerequisite topic to the dependent topic.
    """
    dot = Digraph(comment="Math Academy Knowledge Graph", format="png")
    dot.attr(rankdir="LR")  # Layout from left to right

    # Create subclusters for courses and nested clusters for units.
    for (course_id, course_name), unit_dict in grouped.items():
        with dot.subgraph(name=f"cluster_course_{course_id}") as course_cluster:
            course_cluster.attr(style="filled", color="lightblue")
            course_cluster.attr(label=f"Course: {course_name}")
            for (unit_id, unit_name), topics in unit_dict.items():
                with course_cluster.subgraph(
                    name=f"cluster_unit_{course_id}_{unit_id}"
                ) as unit_cluster:
                    unit_cluster.attr(style="filled", color="lightyellow")
                    unit_cluster.attr(label=f"Unit: {unit_name}")
                    for topic in topics:
                        node_id = f"lesson_{topic['id']}"
                        label = topic.get("name", "")
                        # A lesson is considered done if its 'repetition' is nonzero.
                        repetition = topic.get("repetition", 0)
                        fillcolor = "lightgreen" if repetition else "lightgrey"
                        unit_cluster.node(
                            node_id, label, style="filled", fillcolor=fillcolor
                        )

    # Add edges from prerequisite topics to the current topic.
    for topic in lessons.values():
        current_node = f"lesson_{topic['id']}"
        for prereq in topic.get("prerequisites", []):
            prereq_node = f"lesson_{prereq}"
            if prereq in lessons:
                dot.edge(prereq_node, current_node)
    return dot


def create_unit_graph(lessons):
    """
    Creates a Graphviz Digraph where each node represents a 'unit'.
    An edge is added from unit A to unit B if there exists at least one lesson in unit B
    that has a prerequisite lesson from unit A.
    """
    # Build a dictionary of unique units.
    units = {}
    for topic in lessons.values():
        unit_info = topic.get("unit", {})
        unit_id = unit_info.get("id", "NoUnit")
        unit_name = unit_info.get("name", "No Unit")
        course_info = topic.get("course", {})
        course_id = course_info.get("id", "NoCourse")
        course_name = course_info.get("name", "No Course")
        unit_key = (course_id, unit_id, unit_name)
        if unit_key not in units:
            units[unit_key] = {
                "course_id": course_id,
                "course_name": course_name,
                "unit_id": unit_id,
                "unit_name": unit_name,
            }

    # Build edges between units: For each lesson, examine its prerequisites.
    edges = set()
    for topic in lessons.values():
        current_unit_info = topic.get("unit", {})
        current_unit_id = current_unit_info.get("id", "NoUnit")
        current_unit_name = current_unit_info.get("name", "No Unit")
        current_course_info = topic.get("course", {})
        current_course_id = current_course_info.get("id", "NoCourse")
        current_unit_key = (current_course_id, current_unit_id, current_unit_name)

        for prereq_id in topic.get("prerequisites", []):
            if prereq_id in lessons:
                prereq_topic = lessons[prereq_id]
                prereq_unit_info = prereq_topic.get("unit", {})
                prereq_unit_id = prereq_unit_info.get("id", "NoUnit")
                prereq_unit_name = prereq_unit_info.get("name", "No Unit")
                prereq_course_info = prereq_topic.get("course", {})
                prereq_course_id = prereq_course_info.get("id", "NoCourse")
                prereq_unit_key = (prereq_course_id, prereq_unit_id, prereq_unit_name)
                # Create an edge if the prerequisite unit differs from the current unit.
                if prereq_unit_key != current_unit_key:
                    edges.add((prereq_unit_key, current_unit_key))

    # Create the unit graph using Graphviz.
    dot = Digraph(comment="Math Academy Unit Knowledge Graph", format="png")
    dot.attr(rankdir="LR")  # Layout: left-to-right

    # Add nodes for each unique unit.
    for unit_key, unit_data in units.items():
        node_id = f"unit_{unit_data['course_id']}_{unit_data['unit_id']}".replace(
            " ", "_"
        )
        label = f"{unit_data['course_name']}\nUnit: {unit_data['unit_name']}"
        dot.node(node_id, label, shape="box", style="filled", fillcolor="lightyellow")

    # Add edges between units.
    for edge in edges:
        from_key, to_key = edge
        from_node_id = f"unit_{from_key[0]}_{from_key[1]}".replace(" ", "_")
        to_node_id = f"unit_{to_key[0]}_{to_key[1]}".replace(" ", "_")
        dot.edge(from_node_id, to_node_id)

    return dot


def create_module_graph(lessons):
    """
    Creates a Graphviz Digraph where each node represents a 'module'.
    An edge is added from module A to module B if there exists at least one lesson in module B
    that has a prerequisite lesson from module A.

    - Nodes are labeled with the course and module name.
    - Edges represent prerequisite relationships between modules.
    """
    # Build a dictionary of unique modules.
    modules = {}
    for topic in lessons.values():
        mod_info = topic.get("module", {})
        mod_id = mod_info.get("id", "NoModule")
        mod_name = mod_info.get("name", "No Module")
        course_info = topic.get("course", {})
        course_id = course_info.get("id", "NoCourse")
        course_name = course_info.get("name", "No Course")
        # Use a tuple to uniquely identify a module.
        module_key = (course_id, mod_id, mod_name)
        if module_key not in modules:
            modules[module_key] = {
                "course_id": course_id,
                "course_name": course_name,
                "module_id": mod_id,
                "module_name": mod_name,
            }

    # Build edges between modules: For each lesson, examine its prerequisites.
    edges = set()
    for topic in lessons.values():
        current_mod_info = topic.get("module", {})
        current_mod_id = current_mod_info.get("id", "NoModule")
        current_mod_name = current_mod_info.get("name", "No Module")
        current_course_info = topic.get("course", {})
        current_course_id = current_course_info.get("id", "NoCourse")
        current_module_key = (current_course_id, current_mod_id, current_mod_name)

        for prereq_id in topic.get("prerequisites", []):
            if prereq_id in lessons:
                prereq_topic = lessons[prereq_id]
                prereq_mod_info = prereq_topic.get("module", {})
                prereq_mod_id = prereq_mod_info.get("id", "NoModule")
                prereq_mod_name = prereq_mod_info.get("name", "No Module")
                prereq_course_info = prereq_topic.get("course", {})
                prereq_course_id = prereq_course_info.get("id", "NoCourse")
                prereq_module_key = (prereq_course_id, prereq_mod_id, prereq_mod_name)
                # Create an edge if the prerequisite module differs from the current module.
                if prereq_module_key != current_module_key:
                    edges.add((prereq_module_key, current_module_key))

    # Create the module graph using Graphviz.
    dot = Digraph(comment="Math Academy Module Knowledge Graph", format="png")
    dot.attr(rankdir="LR")  # Layout: left-to-right

    # Add nodes for each unique module.
    for module_key, mod_data in modules.items():
        node_id = f"module_{mod_data['course_id']}_{mod_data['module_id']}".replace(
            " ", "_"
        )
        label = f"{mod_data['course_name']}\nModule: {mod_data['module_name']}"
        dot.node(node_id, label, shape="ellipse", style="filled", fillcolor="lightpink")

    # Add edges between modules.
    for edge in edges:
        from_key, to_key = edge
        from_node_id = f"module_{from_key[0]}_{from_key[1]}".replace(" ", "_")
        to_node_id = f"module_{to_key[0]}_{to_key[1]}".replace(" ", "_")
        dot.edge(from_node_id, to_node_id)

    return dot


def generate_all_graphs(knowledge_graph: dict):
    # Load all topics from the file.
    # topics = load_topics("knowledge-graph.json")
    topics = knowledge_graph["topics"]

    # Generate and render the graph of all lessons.
    full_grouped, full_lessons = group_topics_by_course_and_unit(topics)
    full_graph = create_graph(full_grouped, full_lessons)
    full_output_filename = "math_academy_knowledge_graph"
    full_graph.render(full_output_filename, view=False)
    print(f"Full graph generated as {full_output_filename}.png")

    # Filter topics to only those that are not completed (repetition == 0).
    incomplete_topics = {
        tid: topic for tid, topic in topics.items() if topic.get("repetition", 0) == 0
    }
    incomplete_grouped, incomplete_lessons = group_topics_by_course_and_unit(
        incomplete_topics
    )
    incomplete_graph = create_graph(incomplete_grouped, incomplete_lessons)
    incomplete_output_filename = "math_academy_incomplete_knowledge_graph"
    incomplete_graph.render(incomplete_output_filename, view=False)
    print(f"Incomplete lessons graph generated as {incomplete_output_filename}.png")

    # Create and render the unit knowledge graph.
    unit_graph = create_unit_graph(full_lessons)
    unit_output_filename = "math_academy_unit_knowledge_graph"
    unit_graph.render(unit_output_filename, view=False)
    print(f"Unit knowledge graph generated as {unit_output_filename}.png")

    # Create and render the module knowledge graph.
    module_graph = create_module_graph(full_lessons)
    module_output_filename = "math_academy_module_knowledge_graph"
    module_graph.render(module_output_filename, view=False)
    print(f"Module knowledge graph generated as {module_output_filename}.png")
