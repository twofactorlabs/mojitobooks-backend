# DECKSLASH - BACKEND
----------------------------------
## Set up the environment:
1. Install python 3.
2. Use pip to install these external packages:
  1. flask-restful.
  2. flask-sqlalchemy.
  3. wtforms.
  4. flask-wtf.
  5. flask-marshmallow.
  6. marshmallow-sqlalchemy.
  7. flask-bcrypt.
  8. flask-cors.
  9. flask-jwt-extended.
  10. uuid.
3. Go to the deckslash-backend\Deck_Slash directory: 
  1. run the run.py file.
  => The server will be running on http://127.0.0.1:5000/.
----------------------------------------
## Api Protocol: 
1. For testing only: 
  1. *GET /testuser*: get all users
  2. *GET /testcard*: get all posts
2. For real application: 
  1. Search:
  2. *GET /users/<username>*: get a specific user
  
