import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = 'postgresql://pelcool@localhost:5432/trivia'
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """

    #1 Test for retrieving all categories
    def test_retrieve_categories(self):
        res = self.client().get("/categories")
        data = json.loads(res.data)

        self.assertEqual(data["success"], True)
        self.assertTrue(data["categories"])

    #2 test for retrieving all questions
    def test_retrieve_all_questions(self):
        res = self.client().get("/questions")
        data = json.loads(res.data)

        self.assertEqual(data["success"], True)
        self.assertTrue(data["questions"])
        self.assertTrue(data["total_questions"])
        self.assertTrue(data["current_category"])
    
    

    #3 testing for adding new questions
    def test_for_adding_questions(self):

        new_question = {
        'question': 'What is your name?',
        'answer': 'Comfort',
        'category': '1',
        'difficulty': 1,
        }
        res = self.client().post("/questions",json = new_question)
        data = json.loads(res.data)

        self.assertEqual(data["success"], True)
        self.assertTrue(data["created"])
        self.assertTrue(data["questions"])
        self.assertTrue(data["total_questions"])


    # 4 testing searching for question
    def test_search_questions(self):
        search = {"search_term": 'a'}
        res = self.client().post("/questions/search", json = search)
        data = json.loads(res.data)

        self.assertEqual(data["success"], True)
        self.assertIsNotNone(data["results"])
        self.assertIsNotNone(data["total_questions"])

    #5 test for deleting question using question ID
    def test_for_deleting_question_byID(self):
        question = Question(question="test question", answer="test answer", difficulty=3, category=2)
        question.insert()
        question_id = question.id

        res = self.client().delete("/questions/{question_id}")
        data = json.loads(res.data)

        question = Question.query.filter(Question.id == question_id).one_or_none()

        self.assertEqual(data["success"], True)
        self.assertEqual(data["deleted"],str(question_id))
        self.assertTrue(data["questions"])
        self.assertTrue(data["total_questions"])
    
    # 6 test for retrieving questions based on category
    def test_for_questions_based_on_category(self):
        res = self.client().get("/categories/1/questions")
        data = json.loads(res.data)

        self.assertEqual(data["success"], True)
        self.assertTrue(data["questions"])
        self.assertTrue(data["current_category"])
        self.assertTrue(data["total_questions"])

    # 7 test for playing quiz
    def test_for_playing_quiz(self):
        body = {
            "previous_questions" :[1,5],
            "quiz_category":{
                "id": 4,
                "type": 'History'
            }
        }

        res = self.client().post("/quizzes", json= body)
        data = json.loads(res.data)

        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])
        







# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()