import json
import os
from api import MathAcademyAPI
from generate_graph import generate_all_graphs

pw = os.getenv("MATHACADEMY_PASSWORD")
email = os.getenv("MATHACADEMY_EMAIL")
api = MathAcademyAPI()
api.login(email, pw)

print(json.dumps(api.get_student_xp_goals("4760"), indent=4))
knowledge_graph = api.get_student_course_knowledge_graph("4760", ["114"])
generate_all_graphs(knowledge_graph)
