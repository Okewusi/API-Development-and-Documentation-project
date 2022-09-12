from crypt import methods
import os
from tkinter.messagebox import NO
from unicodedata import category
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

    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    CORS(app)

    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """
    def after_request(response):
        response.headers.add('Access-Control_Allow-Headers','Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Headers', 'GET,POST, PATCH, DELETE, OPTIONS')
        return response

    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.route('/categories')
    def get_categories():
        try:
            all_categories = Category.query.order_by(Category.id).all()
            if len(all_categories) == 0:
                abort(404)
            formatted_categories = [category.format() for category in all_categories]

            return jsonify({
                "success" : True,
                "categories": formatted_categories
            })
        except:
            abort(422)

    QUESTIONS_PER_PAGE = 10

    def paginated_questions(request, all_questions):
        page = request.args.get('page', 1, type=int)
        start = (page-1)* QUESTIONS_PER_PAGE
        end = start + QUESTIONS_PER_PAGE

        questions = [question.format() for question in all_questions]
        current_questions = questions[start: end]

        return current_questions


    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.
    

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """
    

    @app.route('/questions')
    def get_questions():
        try:
            all_questions = Question.query.order_by(Question.id).all()
            current_questions = paginated_questions(request, all_questions)

            return jsonify({
                "success": True,
                "questions": current_questions,
                "total_questions": len(current_questions),
                "current_category": "All"
            })
        except:
            abort(422)


    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """

    @app.route('/questions/<int:question_id>', methods=["DELETE"])
    def delete_question(question_id):
        try:
            question = Question.query.filter(Question.id==question_id).one_or_none()
            if question is None:
                abort(404)
            question.delete()

            all_questions = Question.query.order_by(Question.id).all()
            current_questions = paginated_questions(request, all_questions)
            return jsonify({
                "success": True,
                "deleted":question_id,
                "questions": current_questions,
                "total_questions": len(current_questions)
            })
        except:
            abort(422)

    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.


    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """

    @app.route("/questions", methods=["POST"])
    def create_question():
        body = request.get_json()

        new_question = body.get("question", None)
        new_answer = body.get("answer", None)
        new_category = body.get("category", None)
        new_difficulty = body.get("difficulty", None)

        try:
            question = Question(question=new_question, answer=new_answer, category=new_category, difficulty= new_difficulty)
            question.insert()

            all_questions = Question.query.order_by(Question.id).all()
            current_questions = paginated_questions(request, all_questions)

            return jsonify({
                "success": True,
                "created":question.id,
                "questions": current_questions,
                "total_questions": len(current_questions)
            })
        except:
            abort(422)






    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """

    @app.route('/questions/search', methods=['POST'])
    def search_questions():
        body = request.get_json()
        search_term = body.get('searchTerm', None)

        try:
            search_results = Question.query.filter(Question.question.ilike(f"%{search_term}%")).all()
            formatted_results = [question.format() for question in search_results]

            return jsonify({
                "success" : True,
                "results": formatted_results,
                "total_questions" : len(search_results)
            })
        except:
            abort(422)

    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """

    @app.route('/categories/<int:category_id>/questions')
    def retrieve_questions_by_category(category_id):
        category = Category.query.get(category_id)
        if category is None:
            abort(404)

        try:
            #get questions in selected category 
            questions = Question.query.order_by(Question.id).filter(Question.category== str(category_id)).all()
            current_questions = paginated_questions(request, questions)

            return jsonify({
                "success": True,
                "questions": current_questions,
                "current_category": category.type,
                "total_questions": len(questions)
            })        
        except:
            abort(422)    

    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """

    @app.route('/quizzes', methods=['POST'])
    def play_quiz():

        try:
            body = request.get_json()
            category = body['quiz_category', None]
            previous_questions = body["previous_questions", None]
            

            #if a particular category is selected and if not
            if category['id'] != 0:
                questions = Question.query.filter(Question.category == category["id"]).all()
            else:
                questions = Question.query.all()

            #function for getting random question
            def get_a_random_question():
                next_question = random.choice(questions).format()
                return next_question
            
            next_question = get_a_random_question()

            seen_question = False
            if next_question['id'] in previous_questions:
                seen_question = True
            
            while seen_question:
                next_question = get_a_random_question()

                if (len(previous_questions) == len(questions)):
                    return jsonify({
                    'success': True,
                    'question': "None, game over"
                    })

            return jsonify({
            'success': True,
            'question': next_question
            })
        except:
            abort(422)


    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": 'Bad request'
        }), 400
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": 'Not found'
        }), 404

    @app.errorhandler(422)
    def unprocessable_entity(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": 'Unprocessable Entity'
        }), 422

    return app

