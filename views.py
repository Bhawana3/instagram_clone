from flask import Blueprint, render_template, request, flash, redirect, url_for, session, jsonify
from flask.views import MethodView
from passlib.hash import sha256_crypt
from instagram_clone import alchemy_session
from utils import *
from sqlalchemy import func

from .models import *

views = Blueprint("views", __name__, template_folder= "templates")

class IndexView(MethodView):
    def get(self):
        return "<html>User logged in</html>"


class SignupView(MethodView):
    def get(self):
        return render_template('signup.html')

    def post(self):
        user = User(
            username = request.values.get('username'),
            email = request.values.get('email'),
            password = request.values.get('password')
            )
        try:
            user.save()
        except Exception as e:
            print "error: ",e
            flash('User already registered')
            return redirect(url_for('views.signup'))
        flash('User successfully registered')

        logged_in = perform_login (user.id, request.values.get('email'), request.values.get('username'))

        return redirect(url_for('views.index'))


class LoginView(MethodView):
    def get(self):
        return render_template('login.html')

    def post(self):
        email = request.values.get('email')
        password = request.values.get('password')
        try:
            registered_user = User.query.filter_by(email=email).first()
        except Exception as e:
            print "Database quering error"

        if registered_user is None:
            flash('User does not exist', 'error')
            return redirect(url_for('views.login'))
        else:
            if sha256_crypt.verify(password, registered_user.password):

                logged_in = perform_login (registered_user.id, registered_user.email, registered_user.username)

            else:
                flash('Invalid Credentials !!')
                return redirect(url_for('views.login'))

        # check for email and password combination
        flash('Logged in successfully')
        print session['uid']
        return redirect(url_for('views.profile',uid=session['uid']))

class ProfileView(MethodView):

    """show number of followers ,following count, own posts count , edit profile option """

    def get(self,uid):

        if 'uid' in session:
            following = alchemy_session.query(func.count(Followers.id)).filter(Followers.to_id == session['uid']).scalar()
            followers = alchemy_session.query(func.count(Followers.id)).filter(Followers.from_id == session['uid']).scalar()
            posts = alchemy_session.query(func.count(Photo_details.id)).filter(Photo_details.user_id == session['uid']).scalar()

            return jsonify({'followers':followers, 'following':following, 'posts':posts})

        else:
            return redirect(url_for('views.login'))


class SharePhotoView(MethodView):
    def post(self):
        # upload and share photo with people
        return redirect(url_for('views.feed'))

class FeedView(MethodView):
    def get(self):
        # show own feed and all the updates of followed people
        return render_template('feed.html')

class DiscoverPeopleView(MethodView):
    def get(self):
        # code for discover people
        # show users which are not followed by logged in user
        return render_template('discover.html')

class LogoutView(MethodView):
    def get(self):
        session.clear()
        print "user logged out successfully.",session
        return redirect(url_for('views.login'))




# Register the urls
views.add_url_rule('/', view_func=IndexView.as_view('feed'), methods=['GET','POST'])
views.add_url_rule('/signup', view_func=SignupView.as_view('signup'),methods=['GET','POST'])
views.add_url_rule('/login', view_func=LoginView.as_view('login'),methods=['GET','POST'])
views.add_url_rule('/discover', view_func=DiscoverPeopleView.as_view('discover'), methods=['GET','POST'])
views.add_url_rule('/<uid>', view_func=ProfileView.as_view('profile'), methods=['GET','POST'])
views.add_url_rule('/share', view_func=SharePhotoView.as_view('share'), methods=['GET','POST'])
views.add_url_rule('/logout',view_func=LogoutView.as_view('logout'))
