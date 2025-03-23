import requests
from typing import Optional, Dict, Any, Union
from urllib.parse import urljoin


class MathAcademyAPI:
    BASE_URL = "https://mathacademy.com"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Content-Type": "application/x-www-form-urlencoded",
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                "Origin": self.BASE_URL,
            }
        )

    def _get(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """Make a GET request to the API"""
        url = urljoin(self.BASE_URL, endpoint)
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.json()

    def _post(self, endpoint: str, data: Optional[Dict] = None) -> Dict:
        """Make a POST request to the API"""
        url = urljoin(self.BASE_URL, endpoint)
        response = self.session.post(url, data=data)
        response.raise_for_status()
        return response.json()

    def login(self, username_or_email: str, password: str) -> None:
        """Login to Math Academy"""
        data = {
            "usernameOrEmail": username_or_email,
            "password": password,
            "submit": "LOGIN",
        }
        response = self.session.post(urljoin(self.BASE_URL, "/login"), data=data)
        response.raise_for_status()

    # Dashboard methods
    def get_school(self, school_id: str) -> Dict:
        """Get school information"""
        return self._get(f"/api/dashboard/schools/{school_id}")

    def add_school(self, school: Dict) -> Dict:
        """Add a new school"""
        return self._post("/api/dashboard/schools", school)

    def update_school(self, school: Dict) -> Dict:
        """Update school information"""
        return self._post(f'/api/dashboard/schools/{school["id"]}/update', school)

    def delete_school(self, school_id: str) -> Dict:
        """Delete a school"""
        return self._post(f"/api/dashboard/schools/{school_id}/delete")

    # Code Libraries methods
    def get_code_libraries(self) -> Dict:
        """Get all code libraries"""
        return self._get("/api/code-libraries")

    def get_code_library(self, name: str) -> Dict:
        """Get a specific code library"""
        return self._get(f"/api/code-libraries/{name}")

    def save_code_library(self, name: str, code: str) -> Dict:
        """Save a code library"""
        data = {"name": name, "code": code}
        return self._post(f"/api/code-libraries/{name}", data)

    # Version Upgrade methods
    def accept_version_upgrade(self, student_id: str, course_id: str) -> Dict:
        """Accept version upgrade"""
        data = {"studentId": student_id, "courseId": course_id}
        return self._post(f"/api/courses/{course_id}/accept-version-upgrade", data)

    def decline_version_upgrade(self, student_id: str, course_id: str) -> Dict:
        """Decline version upgrade"""
        data = {"studentId": student_id, "courseId": course_id}
        return self._post(f"/api/courses/{course_id}/decline-version-upgrade", data)

    def acknowledge_version_upgrade(self, student_id: str, course_id: str) -> Dict:
        """Acknowledge version upgrade"""
        data = {"studentId": student_id, "courseId": course_id}
        return self._post(f"/api/courses/{course_id}/acknowledge-version-upgrade", data)

    # Questions methods
    def get_question(self, question_id: str) -> Dict:
        """Get question details"""
        return self._get(f"/api/questions/{question_id}")

    def create_question(self, data: Dict) -> Dict:
        """Create a new question"""
        return self._post("/api/questions/new", data)

    def update_question(self, question_id: str, data: Dict) -> Dict:
        """Update a question"""
        return self._post(f"/api/questions/{question_id}", data)

    def delete_question(self, question_id: str) -> Dict:
        """Delete a question"""
        return self._post(f"/api/questions/{question_id}/delete")

    # XP Goals methods
    def get_student_xp_goals(self, student_id: str) -> Dict:
        """Get XP goals for a student"""
        return self._get(f"/api/students/{student_id}/xp-goals")

    def update_student_xp_goals(self, student_id: str, data: Dict) -> Dict:
        """Update XP goals for a student

        Args:
            student_id: ID of the student
            data: Dictionary containing XP goals data to update
        """
        return self._post(f"/api/students/{student_id}/xp-goals", data)

    def get_student_course_knowledge_graph(
        self, student_id: str, course_ids: list[str]
    ) -> Dict:
        """Get knowledge graph for a student across specified courses

        Args:
            student_id: ID of the student
            course_ids: List of course IDs to get knowledge graph for
        """
        course_id_list = ",".join(course_ids)
        return self._get(
            f"/api/courses/{course_id_list}/students/{student_id}/knowledge-graph"
        )
