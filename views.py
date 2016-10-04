import flask
from flask import Blueprint, render_template, request, flash, redirect, url_for, session, jsonify, json
from flask.views import MethodView
from passlib.hash import sha256_crypt
from instagram_clone import alchemy_session
from utils import *

from sqlalchemy import update
from sqlalchemy.sql import and_,or_

from .models import *
from manage import os

views = Blueprint("views", __name__, template_folder= "templates")

class IndexView(MethodView):
    def get(self):
        return "<html>User logged in</html>"


class SignupView(MethodView):
    def get(self):
        return render_template('signup.html')

    def post(self):
        user = User(
            username=request.values.get('username'),
            email=request.values.get('email'),
            password=request.values.get('password')
            )
        try:
            user.save()
        except Exception as e:
            print "error: ",e
            flash('User already registered')
            return redirect(url_for('views.signup'))
        flash('User successfully registered')

        logged_in = perform_login(user.id, request.values.get('email'), request.values.get('username'))

        return redirect(url_for('views.profile', uid=user.id))


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

                logged_in = perform_login(registered_user.id, registered_user.email, registered_user.username)

            else:
                flash('Invalid Credentials !!')
                return redirect(url_for('views.login'))

        # check for email and password combination
        flash('Logged in successfully')
        return redirect(url_for('views.profile',uid=session['uid']))


class ProfileView(MethodView):

    """show number of followers ,following count, own posts count , edit profile option ,
        own posts """

    """ if logged in user profile then show edit profile option

            otherwise show followers/following option"""

    def get(self,uid):

        if 'uid' in session:

            following = []
            followers = []
            try:
                user_detail = alchemy_session.query(User.username, User.profile_pic).filter(User.id == uid).first()
                print user_detail
                username = user_detail[0]
                profile_pic = user_detail[1]
                print profile_pic

            except Exception as e:
                print "Database quering error"

            try:
                results = alchemy_session.query(Followers.to_id,Followers.from_id).filter(or_(Followers.from_id == uid, Followers.to_id == uid)).all()

            except Exception as e:
                print "Database quering error"

            for result in results:
                print type(result[0])
                if str(result[0]) == str(uid):
                    followers.append(result[1])
                else:
                    following.append(result[0])
            try:
                posts = alchemy_session.query(Photo_details.photo_path).filter(Photo_details.user_id == uid).all()

            except Exception as e:
                print "Database quering error"

            if str(uid) == str(session['uid']):
                uid = str(session['uid'])
                logged_in_user = True
            else:
                uid = str(uid)
                logged_in_user = False

            return render_template('profile.html', followers=len(followers), following=len(following),
                                   posts_count=len(posts), posts=posts, username=username, profile_pic=profile_pic ,
                                   uid=uid, logged_in_user=logged_in_user)

        else:
            return redirect(url_for('views.login'))


class SharePhotoView(MethodView):

    def post(self):
        print "Inside share photo view"
        # For uploading photo
        folder = 'static/uploads'
        allowed_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.JPG']

        # upload and share photo with people
        if 'uid' in session:
            logged_in_user_id = session['uid']
            try:
                if request.method == 'POST':
                    file = request.files['photo']
                    extension = os.path.splitext(file.filename)[1]
                    if extension in allowed_extensions:
                        filename = str(logged_in_user_id) + extension  # filename should be uid + extension
                        file.save(os.path.join(folder, filename))
                        print "Image uploaded:", filename
                        image_path = 'static/uploads/' + filename

                        # update user model with profile pic details
                        logged_in_user_details = User.query.filter_by(id = logged_in_user_id).first()
                        print logged_in_user_details
                        logged_in_user_details.profile_pic = image_path
                        db.session.commit()

                        respStr = json.dumps({'message': 'success'})
                        resp = flask.Response(respStr)
                        resp.headers['Content-Type'] = 'application/json'
                        return resp
                    else:
                        respStr = json.dumps({'message': 'failure'})
                        resp = flask.Response(respStr)
                        resp.headers['Content-Type'] = 'application/json'
                        return resp
                        print "error: image format should be png,jpg,jpeg,gif"
                else:
                    return redirect(url_for('views.profile', uid=logged_in_user_id))
            except Exception as e:
                print e

class FollowingView(MethodView):
    def get(self,uid):
        if 'uid' in session:
            try:
                following = alchemy_session.query(User.username,User.profile_pic).join(Followers, User.id == Followers.to_id).filter(Followers.from_id == uid).all()

            except Exception as e:
                print "Database quering error"
            return render_template('following.html', followings=following)

class FollowersView(MethodView):
    def get(self,uid):
        if 'uid' in session:
            try:
                followers = alchemy_session.query(User.username,User.profile_pic).join(Followers, User.id == Followers.from_id).filter(Followers.to_id == uid).all()
            except Exception as e:
                print "Database quering error"
            return render_template('followers.html',followers=followers)

class FeedView(MethodView):
    def get(self):
        # show own feed and all the updates of followed people
        return render_template('feed.html')

class DiscoverPeopleView(MethodView):
    """code for discovering people,
     show users which are not followed by logged in user"""

    def get(self):
        users = []
        if 'uid' in session:
            logged_in_user_id = session['uid']
            print type(logged_in_user_id)

            # wrong query
            subquery = alchemy_session.query(Followers.to_id).filter(Followers.from_id != logged_in_user_id).group_by(Followers.to_id)
            print subquery
            all_users_except_followed = alchemy_session.query(User).filter(~User.id.in_(subquery))
            print all_users_except_followed
            for user in all_users_except_followed:
                users.append(user.id)
            return jsonify('data',users)

class LogoutView(MethodView):
    def get(self):
        session.clear()
        print "user logged out successfully.",session
        return redirect(url_for('views.login'))




# Register the urls
views.add_url_rule('/', view_func=FeedView.as_view('feed'), methods=['GET','POST'])
views.add_url_rule('/signup', view_func=SignupView.as_view('signup'),methods=['GET','POST'])
views.add_url_rule('/login', view_func=LoginView.as_view('login'),methods=['GET','POST'])
views.add_url_rule('/discover', view_func=DiscoverPeopleView.as_view('discover'), methods=['GET','POST'])
views.add_url_rule('/<uid>', view_func=ProfileView.as_view('profile'), methods=['GET','POST'])
views.add_url_rule('/share', view_func=SharePhotoView.as_view('share'), methods=['GET','POST'])
views.add_url_rule('/<uid>/followers', view_func=FollowersView.as_view('followers'), methods=['GET','POST'])
views.add_url_rule('/<uid>/following', view_func=FollowingView.as_view('following'), methods=['GET','POST'])
views.add_url_rule('/logout',view_func=LogoutView.as_view('logout'))
