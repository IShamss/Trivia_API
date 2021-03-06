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
        self.database_path = "postgres://{}/{}".format(
            'localhost:5433', self.database_name)
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

    def test_get_paginated_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['categories'])
        self.assertEqual(data['current_category'], None)

    def test_404_requesting_beyond_valid_page(self):
        res = self.client().get('/questions?page=1000')
        data = json.loads(res.data)

        self.assertFalse(data['success'])
        self.assertEqual(data['message'], "resource not found")
        self.assertEqual(res.status_code, 404)

    def test_delete_question(self):

        res = self.client().delete('/questions/1')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertAlmostEqual(data['success'], True)
        self.assertEqual(data['deleted'], '1')

    def test_404_delete_book_not_exist(self):
        res = self.client().delete('/questions/1000')
        data = json.loads(res.data)

        self.assertFalse(data['success'])
        self.assertEqual(data['message'], "resource not found")
        self.assertEqual(res.status_code, 404)

    def test_post_question(self):
        res = self.client().post(
            '/questions',
            json={
                'question': 'test question',
                'answer': 'test answer',
                'category': '4',
                'difficulty': 1})
        data = json.loads(res.data)

        self.assertEqual(data['success'], True)
        self.assertTrue('created')

    def test_search_questions_with_results(self):
        res = self.client().post('/questions', json={'searchTerm': 'the'})
        data = json.loads(res.data)
        self.assertTrue(data['success'])
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['total_questions'])
        self.assertEqual(data['current_category'], None)

    def test_search_questions_without_results(self):
        res = self.client().post(
            '/questions',
            json={
                'searchTerm': 'fullstackapp'})
        data = json.loads(res.data)

        self.assertTrue(data['success'])
        self.assertFalse(data['questions'])
        self.assertEqual(data['current_category'], None)
        self.assertFalse(data['total_questions'])
        self.assertEqual(res.status_code, 200)

    def test_get_questions_based_categories(self):
        res = self.client().get('/categories/4/questions')
        data = json.loads(res.data)

        self.assertTrue(data['questions'])
        self.assertTrue(data['success'])
        self.assertEqual(data['current_category'], 4)
        self.assertTrue(data['total_questions'])
        self.assertEqual(res.status_code, 200)

    def test_404_questions_based_categories(self):
        res = self.client().get('/categories/10000/questions')
        data = json.loads(res.data)

        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "resource not found")
        self.assertEqual(res.status_code, 404)

    def test_quiz(self):
        res = self.client().post(
            '/quizzes',
            json={
                'previous_questions': [],
                'quiz_category': {
                    'type': 'History',
                    'id': 5}})
        data = json.loads(res.data)

        self.assertTrue(data['success'])
        self.assertTrue(data['question'])
        self.assertEqual(res.status_code, 200)

    def test_422_quiz(self):
        res = self.client().post('/quizzes')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['message'], "unprocessable")
        self.assertFalse(data['success'])


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
