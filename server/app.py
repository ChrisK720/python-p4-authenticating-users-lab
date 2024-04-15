#!/usr/bin/env python3

from flask import Flask, make_response, jsonify, request, session
from flask_migrate import Migrate
from flask_restful import Api, Resource

from models import db, Article, User

app = Flask(__name__)
app.secret_key = b'Y\xf1Xz\x00\xad|eQ\x80t \xca\x1a\x10K'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)

class ClearSession(Resource):

    def delete(self):
    
        session['page_views'] = None
        session['user_id'] = None

        return {}, 204

class IndexArticle(Resource):
    
    def get(self):
        articles = [article.to_dict() for article in Article.query.all()]
        return articles, 200

class ShowArticle(Resource):

    def get(self, id):
        session['page_views'] = 0 if not session.get('page_views') else session.get('page_views')
        session['page_views'] += 1

        if session['page_views'] <= 3:

            article = Article.query.filter(Article.id == id).first()
            article_json = jsonify(article.to_dict())

            return make_response(article_json, 200)

        return {'message': 'Maximum pageview limit reached'}, 401
class Login(Resource):

    def post(self):
        user = User.query.filter(User.username == request.json['username']).first()
        if not user:
            return make_response({'message':'username not valid, unauthorised'}, 401)
        session['user_id'] = user.id
        return make_response(user.to_dict(), 200)

class Logout(Resource):
    def delete(self):
        session['user_id'] = None
        return make_response({}, 204)

class CheckSession(Resource):
    def get(self):
        user_id = session.get('user_id')
        
        if not user_id:
            return make_response({}, 401)
        user = User.query.filter_by(id = user_id).first()
        if not user:
            make_response({'message':'Not sure why user was not found ask engineer'}, 404)
        
        return make_response(user.to_dict(), 200)
class Practice(Resource):
    def get(self):
        session['practicing'] = session.get('practicing') or False
        session['count'] = session.get('count') or 1
        if not session['practicing']:
            
            session['practicing'] = True
            try:
                response = {
                    'session': {
                        'username': session['user_id'],
                        'message': f"You have loged in and your user_id is shown here {session['count']}"
                    },
                    'cookies': [{cookie: request.cookies[cookie]} for cookie in request.cookies]
                }
                session['count'] += 1
                
                return make_response(response, 200)

            except KeyError:
                return make_response({'message':'You need to first login use the url http://127.0.0.1:5555/Login'})
            # response.set_cookie('Pillar','practice_cookie')
            # response.set_cookie('Cornerstone','this may be your first time on this page')
            # return make_response(response, 200)
            

        
        session['practicing'] = not session['practicing']
        response = {'message':f'This is not your first time logging on'}
        resp = make_response(response, 200)
        resp.set_cookie('another_cookie','hello')
        if session['count'] > 2:
            return make_response({'message':'enough practice now continue'}) 
        return resp


        


api.add_resource(ClearSession, '/clear')
api.add_resource(IndexArticle, '/articles')
api.add_resource(ShowArticle, '/articles/<int:id>')
api.add_resource(Login, '/login')
api.add_resource(Logout,'/logout')
api.add_resource(CheckSession,'/check_session')
api.add_resource(Practice, '/practice')


if __name__ == '__main__':
    app.run(port=5555, debug=True)

# For our basic login feature, we'll need the following functionality:

# A user can log in by providing their username in a form.
# A user can log out.
# A user can remain logged in, even after refreshing the page.
# We'll need to create the resources to handle each of these features. Let's get started!

# NOTE: This lab uses the Flask-Restful module rather than vanilla Flask. You do not need to use it to pass the tests, but we recommend giving it a shot.
# Sessions
# Generate these resources:

# Login is located at /login.

# It has one route, post().
# post() gets a username from request's JSON.
# post() retrieves the user by username (we made these unique for you).
# post() sets the session's user_id value to the user's id.
# post() returns the user as JSON with a 200 status code.
# Logout is located at /logout.

# It has one route, delete().
# delete() removes the user_id value from the session.
# delete() returns no data and a 204 (No Content) status code.
# CheckSession is located at /check_session.

# It has one route, get().
# get() retrieves the user_id value from the session.
# If the session has a user_id, get() returns the user as JSON with a 200 status code.
# If the session does not have a user_id, get() returns no data and a 401 (Unauthorized) status code