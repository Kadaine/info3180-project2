"""
Flask Documentation:     http://flask.pocoo.org/docs/
Jinja2 Documentation:    http://jinja.pocoo.org/2/documentation/
Werkzeug Documentation:  http://werkzeug.pocoo.org/documentation/
This file creates your application.
"""

from app import app, filefolder, db, Allowed_Uploads,login_manager
from flask import render_template, request, jsonify, request, redirect, url_for, flash,session, abort, send_from_directory, jsonify, g
from forms import UploadForm, SignupForm,PostForm,LoginForm
from models import UserProfile, UserPost, UserLikes, UserFollows
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.utils import secure_filename
import os
import datetime
# Using JWT
import jwt
from flask import _request_ctx_stack
from functools import wraps
import base64

###
# Routing for your application.
###
def requires_auth(f):
  @wraps(f)
  def decorated(*args, **kwargs):
    auth = request.headers.get('Authorization', None)
    if not auth:
      return jsonify({'code': 'authorization_header_missing', 'description': 'Authorization header is expected'}), 401

    parts = auth.split()

    if parts[0].lower() != 'bearer':
      return jsonify({'code': 'invalid_header', 'description': 'Authorization header must start with Bearer'}), 401
    elif len(parts) == 1:
      return jsonify({'code': 'invalid_header', 'description': 'Token not found'}), 401
    elif len(parts) > 2:
      return jsonify({'code': 'invalid_header', 'description': 'Authorization header must be Bearer + \s + token'}), 401

    token = parts[1]
    try:
         payload = jwt.decode(token, app.config['SECRET_KEY'])
         get_user = UserProfile.query.filter_by(id=payload['user_id']).first()

    except jwt.ExpiredSignature:
        return jsonify({'code': 'token_expired', 'description': 'token is expired'}), 401
    except jwt.DecodeError:
        return jsonify({'code': 'token_invalid_signature', 'description': 'Token signature is invalid'}), 401

    g.current_user = user = get_user
    return f(*args, **kwargs)

  return decorated


@app.route('/')
def index():
    """Render website's initial page and let VueJS take over."""
    return render_template('index.html')
    
    
@app.route('/about/')
def about():
    """Render the website's about page."""
    return render_template('index.html')
    
    
@app.route('/api/users/<user_id>/posts', methods=['POST'])
def upload(user_id):
    form=PostForm()
    if request.method == "POST" and form.validate_on_submit():
        caption = request.form['caption']
        file = request.files['upload']
        now = str(datetime.date.today())
        Filename = secure_filename(file.filename)
        post = UserPost(user_id,Filename,caption,now)
        db.session.add(post)
        db.session.commit()
        file.save(os.path.join(filefolder, Filename))
        result = [{'message': 'File Upload Successful'}]
        return jsonify(result=result)
    else:
        result = [{'message': 'File Upload unsuccessful'}]
        return jsonify(result=result)
            
    error_record = form_errors(form)
    error = [{'error': error_record}]
    return  jsonify(errors=error)
    
    
    
@app.route('/api/users/<user_id>/posts', methods=['GET'])
@requires_auth
def get_user_post(user_id):
    if (int(user_id) == session['userid']):
        user_posts = UserPost.query.filter_by(user_id=user_id).all()
        if user_posts is not None:
            output = []
            for post in user_posts:
                user = UserProfile.query.filter_by(id = user_id).first()
                
                post_data= {"id":post.post_id,"userid": post.user_id,"profile_photo": user.profile_photo, "photo_name": post.photo_name, "caption": post.caption, "created_on": post.created_on}
                output.append(post_data)
            return jsonify({"firstname":user.first_name,"lastname":user.last_name,'profile_photo':user.profile_photo,"location":user.location,"biography":user.biography,"joined_on":user.joined_on.strftime("%B %Y"),"isuser":True,'posts':output})
    else:
        user_posts = UserPost.query.filter_by(user_id=user_id).all()
        if user_posts is not None:
            output = []
            for post in user_posts:
                user = UserProfile.query.filter_by(id = user_id).first()
                
                post_data= {"id":post.post_id,"userid": post.user_id,"profile_photo": user.profile_photo, "photo_name": post.photo_name, "caption": post.caption, "created_on": post.created_on}
                output.append(post_data)
            return jsonify({"firstname":user.first_name,"lastname":user.last_name,'profile_photo':user.profile_photo,"location":user.location,"biography":user.biography,"joined_on":user.joined_on.strftime("%B %Y"),'posts':output})
        
        
            
    
    
    
@app.route("/api/auth/register", methods=["POST"])
def register():
    form = SignupForm()
    if request.method == "POST" and form.validate_on_submit():
        username = request.form['username']
        password = form.password.data
        firstname = form.firstname.data
        lastname = form.lastname.data
        email =  form.email.data
        location = form.location.data
        biography = form.biography.data
        file = request.files['upload']
        now = str(datetime.date.today())
        
        Filename = secure_filename(file.filename)
        user = UserProfile(username,password,firstname,lastname,email,location,biography,Filename,now)
        db.session.add(user)
        db.session.commit()
        file.save(os.path.join(filefolder, Filename))
        result = [{'message': 'File Upload Successful'}]
        return jsonify(result=result)
    error_record = form_errors(form)
    error = [{'error': error_record}]
    return  jsonify(errors=error)
    
    
@app.route('/api/posts', methods=['GET'])
@requires_auth
def get_all_post():
    if request.method == 'GET':
        all_posts = UserPost.query.order_by(UserPost.created_on).all()
        if all_posts is not None:
            output = []
            for post in all_posts:
                user = UserProfile.query.filter_by(id = post.user_id).first()
                post_data= {"user_id": post.user_id, "username": user.username, "profile_photo": user.profile_photo, "photo_name": post.photo_name, "caption": post.caption, "created_on": post.created_on.strftime("%B %Y")}
                output.append(post_data)
            return jsonify({'posts':output})
        else:
            return jsonify({'message':'no post found'})
        
    
    
def get_uploaded_images():
    Images = []
    Load_files = os.listdir('./app/static/uploads/')
    for file in Load_files:
        if file.split('.')[-1] in Allowed_Uploads:
            Images.append(file)
    return Images
    
@app.route("/api/auth/login", methods=["POST"])
def login():
    form = LoginForm()
    if request.method == "POST" and form.validate_on_submit():
        
        if form.username.data:
            username=form.username.data
            password=form.password.data
            user = UserProfile.query.filter_by(username=username, password=password).first()
            
            if user is not None:
                login_user(user)
                #flash('Logged in successfully.')
                session["logged_in"] = True
                session["userid"] = user.id
                payload = {'user_id': user.id}
                token = jwt.encode(payload, app.config['SECRET_KEY'])
                return jsonify(data={'token': token, 'user_id':user.id},success={"Success":"True"})
            else:
                return jsonify({'message': 'incorrect username or password'})
                
    error_record = form_errors(form)
    error = [{'error': error_record}]
    return  jsonify(errors=error)

@app.route("/api/auth/logout",  methods=["GET"])
@requires_auth
def logout():
    g.current_user = None
    return jsonify(message='logout')
    
    
    
    
@app.route('/api/users/<user_id>/followersnumber',methods=["GET"])
@requires_auth
def followersnumber(user_id):
    numberfollow = UserFollows.query.filter_by(user_id=user_id).all()
    numberoffollower=[]
    for number in numberfollow:
        num = {'test': "counted"}
        numberoffollower.append(num)
    return jsonify (follower= numberoffollower)
    
@app.route('/api/users/<user_id>/following',methods=["GET"])
@requires_auth
def followercheck(user_id):
    followcheck = UserFollows.query.filter_by(user_id=user_id, follower_id=session['user_id']).first()
    if(followcheck is None):
        return jsonify (following= False)
    return jsonify (following= True)
    
@app.route('/api/users/<user_id>/follow',methods=["POST"])
@requires_auth
def create_follow(user_id):
    follow = UserFollows(user_id = user_id, follower_id=session['user_id'])
    db.session.add(follow)
    db.session.commit()
    return jsonify (message= 'You followed a user')

# Here we define a function to collect form errors from Flask-WTF
# which we can later use
def form_errors(form):
    error_messages = []
    """Collects form errors"""
    for field, errors in form.errors.items():
        for error in errors:
            message = u"Error in the %s field - %s" % (
                    getattr(form, field).label.text,
                    error
                )
            error_messages.append(message)

    return error_messages
    
    
# user_loader callback. This callback is used to reload the user object from
# the user ID stored in the session
@login_manager.user_loader
def load_user(id):
    return UserProfile.query.get(int(id))


###
# The functions below should be applicable to all Flask apps.
###


@app.route('/<file_name>.txt')
def send_text_file(file_name):
    """Send your static text file."""
    file_dot_text = file_name + '.txt'
    return app.send_static_file(file_dot_text)


@app.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also tell the browser not to cache the rendered page. If we wanted
    to we could change max-age to 600 seconds which would be 10 minutes.
    """
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response


@app.errorhandler(404)
def page_not_found(error):
    """Custom 404 page."""
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port="8080")
