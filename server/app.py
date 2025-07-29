#!/usr/bin/env python3

from flask import Flask, make_response, jsonify, request, session
from flask_migrate import Migrate
from flask_restful import Api, Resource

from models import db, Article, User, ArticlesSchema, UserSchema

# Initialize Flask App and config
app = Flask(__name__)
app.secret_key = b'Y\xf1Xz\x00\xad|eQ\x80t \xca\x1a\x10K'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

# Initialize database and migration support
migrate = Migrate(app, db)
db.init_app(app)

# Initialize API
api = Api(app)


class ClearSession(Resource):

    def delete(self):

        session['page_views'] = None
        session['user_id'] = None

        return {}, 204


class IndexArticle(Resource):

    def get(self):
        articles = [ArticlesSchema().dump(article)
                    for article in Article.query.all()]
        return articles, 200


class ShowArticle(Resource):

    def get(self, id):
        session['page_views'] = 0 if not session.get(
            'page_views') else session.get('page_views')
        session['page_views'] += 1

        if session['page_views'] <= 3:

            article = Article.query.filter(Article.id == id).first()
            article_json = ArticlesSchema.dump(article)

            return make_response(article_json, 200)

        return {'message': 'Maximum pageview limit reached'}, 401

# Logs in user by username and stores user_id in session


class Login(Resource):
    def post(self):
        data = request.get_json()
        username = data.get('username')

        user = User.query.filter_by(username=username).first()

        if user:
            session['user_id'] = user.id
            return UserSchema().dump(user), 200

        # Handle user not found
        return {'message': 'User not found'}, 404

# Logs out user by removing user_id from session


class Logout(Resource):
    def delete(self):
        session['user_id'] = None
        return {}, 204

# Returns logged-in user if session has user_id


class CheckSession(Resource):
    def get(self):
        user_id = session.get('user_id')

        if user_id:
            user = User.query.get(user_id)
            return UserSchema().dump(user), 200

        return {}, 401  # Not authorized


# Register all API routes
api.add_resource(ClearSession, '/clear')
api.add_resource(IndexArticle, '/articles')
api.add_resource(ShowArticle, '/articles/<int:id>')
api.add_resource(Login, '/login')
api.add_resource(Logout, '/logout')
api.add_resource(CheckSession, '/check_session')

# Run server
if __name__ == '__main__':
    app.run(port=5555, debug=True)
