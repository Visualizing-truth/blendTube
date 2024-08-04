from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import Room, User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user

auth = Blueprint('auth', __name__)

@auth.route('/enterRoom', methods=['GET', 'POST'])
def enterRoom():
    if request.method == 'POST':
        roomName = request.form.get('roomName')
        password = request.form.get('password1')
        username = request.form.get('username')
        if not(password):
            #password is null
            flash("Please enter password", category='error')
            
        
        room = Room.query.filter_by(roomName=roomName).first()
        if room:#Room exists
            if check_password_hash(room.password, password):
                
                flash("Logged in successfully", category='success')
                
                # if user does not exist in the room then add them to the database
                for user in room.users:
                    if username == user.username:
                        login_user(user, remember=True)
                        return redirect(url_for('views.home'))
                
                new_user = User(username=username, room_id=room.id)
                db.session.add(new_user)
                db.session.commit()
                login_user(new_user, remember=True)
                        
                return redirect(url_for('views.home'))
            else:
                flash("Incorrect password", category='error')
        
        else:
            flash("Room does not exist in the database.", category='error')
        
    return render_template("enterRoom.html", user= current_user)

@auth.route('/logout')
def logout():
    print("this is working")
    logout_user()
    return redirect(url_for('auth.enterRoom'))
    

@auth.route('/createRoom', methods=['GET', 'POST'])
def createRoom():
    if request.method == 'POST':
        roomName = request.form.get('roomName')
        username = request.form.get('username')
        roomPassword1 = request.form.get('roomPassword1')
        password2 = request.form.get('password2')
        room = Room.query.filter_by(roomName=roomName).first()
        if room:
            flash("Room already exists.", category='error')
        elif len(roomName) < 4:
            flash('Room name must be greater than 3 characters.', category='error')
        elif roomPassword1 != password2:
            flash('Passwords don\'t match.', category='error')
        elif len(username) < 4:
            flash('Username must be greater than 3 characters.', category='error')
        elif len(roomPassword1) < 7:
            flash('Password must be at least 7 characters.', category='error')
        else:
            new_room = Room(roomName=roomName, password=generate_password_hash(roomPassword1, method='pbkdf2:sha256'))
            db.session.add(new_room)
            db.session.commit()
            
            new_user = User(username=username, room_id=new_room.id)
            db.session.add(new_user)
            db.session.commit()
            
            login_user(new_user, remember=True)
            
            flash('Room created!', category='success')
            return redirect(url_for('views.home'))
        
    return render_template("createRoom.html", user=current_user)
