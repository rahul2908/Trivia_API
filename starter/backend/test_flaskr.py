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
        self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
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
    def test_get_all_categories(self):
        response = self.client().get('/categories')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['categories']))

    
    def test_get_categories_fail(self):
        response = self.client().get('/categories/77777')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Resource Not Found')

    
    def test_get_questions(self):
        response = self.client().get('/questions')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['categories']))
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['total_questions'])

    
    def test_get_questions_fail(self):
        response = self.client().get('/questions?page=50000')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Resource Not Found')

    
    def test_delete_questions(self):
        question = Question(question='new_question',
                            answer='new_answer',
                            difficulty=1,
                            category=1)
        question.insert()
        question_id = question.id
        response = self.client().delete(f'/questions/{question_id}')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], question_id)

    
    def test_delete_questions_fail(self):
        response = self.client().delete(f'/questions/q')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Resource Not Found')

    
    def test_post_question(self):
        new_quest = {
                        'question': 'new question',
                        'answer': 'new answer',
                        'category': '1',
                        'difficulty': 1  
                    }
        total_questions = len(Question.query.all())
        response = self.client().post('/questions', json=new_quest)
        data = json.loads(response.data)
        new_total_questions = len(Question.query.all())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(new_total_questions, total_questions+1)


    def test_post_question_fail(self):
        new_quest = {
                        'question': 'new_question',
                        'answer': 'new_answer',
                        'difficulty': 1
                    }
        response = self.client().post(f'/questions', json=new_quest)
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable')

    
    def test_search_questions(self):
        search = {'searchTerm': 'a'}
        response = self.client().post('/questions/search', json=search)
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(len(data['questions']), 10)

    
    def test_search_questions_fail(self):
        search = {'searchTerm': ''}
        response = self.client().post('/questions/search', json=search)
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable')


    def test_get_questions_by_category(self):
        response = self.client().get('/categories/1/questions')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertNotEqual(len(data['questions']), 0)
        self.assertEqual(data['current_category'], 'Science')

    
    def test_get_questions_by_category_fail(self):
        response = self.client().get('/categories/1000/questions')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Bad Request')

    
    def test_play_quiz_questions(self):
        request_data = {
            'previous_questions': [5, 9],
            'quiz_category': {
                'type': 'History',
                'id': 4
            }
        }
        response = self.client().post('/quizzes', json=request_data)
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])
        self.assertNotEqual(data['question']['id'], 5)
        self.assertNotEqual(data['question']['id'], 9)
        self.assertEqual(data['question']['category'], 4)


    def test_play_quiz_questions_fail(self):
        response = self.client().get('/quizzes', json={})
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 405)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Method Not Found')

        

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()