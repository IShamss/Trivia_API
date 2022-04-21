import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
    cors = CORS(app, resources={"/": {"origins": "*"}})
    '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
    @app.after_request
    def after_request(response):
        response.headers.add(
            'Access-Control-Allow-Headers',
            'Content-Type,Authorization,true')
        response.headers.add(
            'Access-Control-Allow-Methods',
            'GET,PUT,POST,DELETE,OPTIONS')
        return response
    '''
  @TODO:
  Create an endpoint to handle GET requests
  for all available categories.
  '''
    @app.route('/categories')
    def retrieve_categories():
        selection = Category.query.order_by(Category.id).all()
        categories = [cat.format() for cat in selection]
        # get all categories then formatting them properly
        return jsonify({
            'success': True,
            'categories': categories,
            'total_categories': len(categories)
        })

    # paginate the pages where questions per page are 10
    def paginate(request, selection):
        page = request.args.get('page', 1, type=int)
        start = (page - 1) * QUESTIONS_PER_PAGE
        end = start + QUESTIONS_PER_PAGE

        questions = [question.format() for question in selection]
        current_questions = questions[start:end]

        return current_questions

    '''
  @TODO:
  Create an endpoint to handle GET requests for questions,
  including pagination (every 10 questions).
  This endpoint should return a list of questions,
  number of total questions, current category, categories.

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions.
  '''
    @app.route('/questions', methods=['GET'])
    def get_questions():
        selection = Question.query.all()
        current_questions = paginate(request, selection)
        categories = Category.query.all()
        formatted_cat = [cat.format() for cat in categories]
        # get all questions and categories and paginating these questions using
        # the paginate user defined function
        if len(current_questions) == 0:
            abort(404)
        # since we are displaying all questions then we don't have current
        # category
        return jsonify({
            'success': True,
            'questions': current_questions,
            'total_questions': len(selection),
            'categories': formatted_cat,
            'current_category': None
        })
    '''
  @TODO:
  Create an endpoint to DELETE question using a question ID.

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page.
  '''

    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        question = Question.query.filter(
            Question.id == question_id).one_or_none()
      # delete a question and if that question doesn't exist abort with status
      # code 404
        if question is None:
            abort(404)

        question.delete()

        return jsonify({
            'success': True,
            'deleted': str(question_id)

        })

    '''
  @TODO:
  Create an endpoint to POST a new question,
  which will require the question and answer text,
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab,
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.
  '''

    @app.route('/questions', methods=['POST'])
    def create_question():

        body = request.get_json()
        if body.get('searchTerm'):
            search = body.get('searchTerm')

            selection = Question.query.filter(
                Question.question.ilike(f'%{search}%')).all()
            current_questions = paginate(request, selection)

            return jsonify({
                'success': True,
                'questions': current_questions,
                'total_questions': len(selection),
                'current_category': None
            })
        else:
            new_question = body.get('question', None)
            new_answer = body.get('answer', None)
            new_category = body.get('category', None)
            new_difficulty = body.get('difficulty', None)
            # get the data from the request then create a new question
            try:
                question = Question(
                    question=new_question,
                    answer=new_answer,
                    category=new_category,
                    difficulty=new_difficulty)
                question.insert()
                return jsonify({
                    'success': True,
                    'created': question.id
                })

            except BaseException:
                abort(422)

    '''
  @TODO:
  Create a POST endpoint to get questions based on a search term.
  It should return any questions for whom the search term
  is a substring of the question.

  TEST: Search by any phrase. The questions list will update to include
  only question that include that string within their question.
  Try using the word "title" to start.
  '''

    # @app.route('/questions/search', methods=['POST'])
    # def search_post():
    #     body = request.get_json()
    #     search = body.get('search_term')

    #     selection = Question.query.filter(
    #         Question.question.ilike(f'%{search}%')).all()
    #     current_questions = paginate(request, selection)

    #     return jsonify({
    #         'success': True,
    #         'questions': current_questions,
    #         'total_questions': len(selection),
    #         'current_category': None
    #     })

    '''
  @TODO:
  Create a GET endpoint to get questions based on category.

  TEST: In the "List" tab / main screen, clicking on one of the
  categories in the left column will cause only questions of that
  category to be shown.
  '''
    # get questions within a certain category
    @app.route('/categories/<int:category_id>/questions', methods=['GET'])
    def get_questions_based_categories(category_id):
        try:
            selection = Question.query.filter(
                Question.category == str(category_id)).all()
            formatted_questions = paginate(request, selection)

            if selection:

                return jsonify({
                    'success': True,
                    'questions': formatted_questions,
                    'total_questions': len(selection),
                    'current_category': category_id
                })
            else:
                abort(404)
        except BaseException:
            abort(404)

    '''
  @TODO:
  Create a POST endpoint to get questions to play the quiz.
  This endpoint should take category and previous question parameters
  and return a random questions within the given category,
  if provided, and that is not one of the previous questions.

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not.
  '''

    @app.route('/quizzes', methods=['POST'])
    def get_quiz():
        try:
            body = request.get_json()
            if not ('quiz_category' in body and 'previous_questions' in body):
                abort(422)
            category = body.get('quiz_category')
            previous_questions = body.get('previous_questions')
            # if the user select the type all
            if category['type'] == 'click':
                questions = Question.query.filter(
                    Question.id.notin_(previous_questions)).all()
            # if the user selected any other type
            else:
                questions = Question.query.filter(
                    Question.category == category['id'],
                    Question.id.notin_(previous_questions)).all()

            new_question = questions[random.randrange(
                0, len(questions))].format() if len(questions) > 0 else None

            return jsonify({
                'success': True,
                'question': new_question
            })
        except BaseException:
            abort(422)

    '''
  @TODO:
  Create error handlers for all expected errors
  including 404 and 422.
  '''
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "bad request"
        }), 400

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "unprocessable"
        }), 422

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "resource not found"
        }), 404

    return app
