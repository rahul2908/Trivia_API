import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

#Pagination
def paginate_questions(request, selection):
  page = request.args.get('page', 1, type=int)
  start =  (page - 1) * QUESTIONS_PER_PAGE
  end = start + QUESTIONS_PER_PAGE
  questions = [question.format() for question in selection]
  current_questions = questions[start:end]

  return current_questions

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  
  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  CORS(app, resources={'/': {'origins': '*'}})

  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response


  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route('/categories')
  def get_all_categories():

    #Getting all the categories 
    categories = Category.query.order_by(Category.type).all()
    
    #If no category found then abort 404(Not Found)
    if len(categories) == 0:
      abort(404)

    return jsonify({
      'success': True,
      'categories': {category.id: category.type for category in categories}
    })

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
  
  @app.route('/questions')
  def get_questions():

    categories = Category.query.order_by(Category.type).all()
    selection = Question.query.order_by(Question.id).all()
    current_questions = paginate_questions(request, selection)
    
    #If no category found then abort 404(Not Found)
    if len(current_questions) == 0:
      abort(404)

    return jsonify({
      'success': True,
      'questions': current_questions,
      'total_questions': len(selection),
      'categories': {category.id: category.type for category in categories},
      'current category': None
    })

  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''

  @app.route('/questions/<int:ques_id>', methods=['DELETE'])
  def delete_question(ques_id):
    try:
      question = Question.query.filter(Question.id == ques_id).one_or_none()

      if question is None:
        abort(404)

      #Delete the question
      question.delete()
      selection = Question.query.order_by(Question.id).all()
      current_questions = paginate_questions(request, selection)

      return jsonify({
        'success': True,
        'deleted': ques_id,
        'questions': current_questions,
        'total_questions': len(Question.query.all())
      })

    except:
      abort(422)


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
  def post_question():

    data = request.get_json()
    if not ('question' in data and 'answer' in data and 'difficulty' in data and 'category' in data):
      abort(422)

    new_question = data.get('question')
    new_answer = data.get('answer')
    new_category = data.get('category')
    new_difficulty = data.get('difficulty')
    
    try:
      question = Question(question=new_question, answer=new_answer, category=new_category, difficulty=new_difficulty)
      #Inserts a new question
      question.insert()
      
      return jsonify({
        'success': True,
        'created': question.id
      })

    except:
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
  @app.route('/questions/search', methods=['POST'])
  def search_questions():

    data = request.get_json()
    search_term = data.get('searchTerm', '')

    if search_term == '':
      abort(422)

    try:
      questions = Question.query.filter(Question.question.ilike(f'%{search_term}%')).all()

      if len(questions) == 0:
        abort(404)

      current_questions = paginate_questions(request, questions)

      return jsonify({
          'success': True,
          'questions': current_questions,
          'total_questions': len(Question.query.all())
        })

    except:
      abort(404)
    
  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''

  @app.route('/categories/<int:category_id>/questions')
  def get_questions_by_category(category_id):

    #Get the category through id
    category = Category.query.filter_by(id=category_id).one_or_none()

    if category is None:
        abort(400)

    selection = Question.query.filter_by(category=category.id).all()
    current_questions = paginate_questions(request, selection)

    return jsonify({
      'success': True,
      'questions': current_questions,
      'total_questions': len(Question.query.all()),
      'current_category': category.type
    })

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
  def play_quiz_questions():
    data = request.get_json()
    previous_questions = data.get('previous_questions')
    quiz_category = data.get('quiz_category')

    if((previous_questions is None) or (quiz_category is None)):
      abort(400)

    if quiz_category['id'] == 0:
      questions = Question.query.all()
    else:
      questions = Question.query.filter_by(category=quiz_category['id']).all()
    
    def random_question():
      return questions[random.randint(0, len(questions)-1)]

    next_ques = random_question()

    flag=True

    while flag:
      if next_ques.id in previous_questions:
        next_ques=random_question()
      else:
        flag=False
    
    return jsonify({
      'success': True,
      'question': next_ques.format()
    })


  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''

  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "Resource Not Found"
    }), 404
    
  @app.errorhandler(422)
  def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422
    
  @app.errorhandler(400)
  def bad_request(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": "Bad Request"
    }), 400
  
  @app.errorhandler(405)
  def method_not_found(error):
    return jsonify({
        "success": False,
        "error": 405,
        "message": "Method Not Found"
    }), 405
  
  return app

    