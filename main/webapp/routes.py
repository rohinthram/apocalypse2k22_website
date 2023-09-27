from flask import  render_template, flash, redirect, url_for, request, jsonify
from webapp import app, db, bcrypt

from webapp.forms import *
from webapp.models import User, Events

from flask_login import login_user, current_user, logout_user, login_required

import hashlib
hash_file = hashlib.sha256()

import json

from datetime import datetime

events_dict = json.load(open('tech_events.json'))
events_dict.update(json.load(open('non_tech_events.json')))
events_dict.update(json.load(open('title_event.json')))
events_dict.update(json.load(open('workshops.json')))
try:
    result_dict = json.load(open('event_results.json'))
except:
    result_dict = {} # if unable to load file, it means result not declared, this IS TO BE CHANGED, this is not good way to say result not declated
@app.route('/')
def home():
    event_types = json.load(open('event_types.json'))
    return render_template('home.html', title='', event_types=event_types)

@app.route('/signup', methods=["GET", "POST"])
def signup():
    if current_user.is_authenticated:
        flash('Already Logged In. Please Log Out to Register', 'info')
        return redirect(url_for('dashboard'))

    form = SignUpForm()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(
            name=form.name.data,
            email=form.email.data,
            reg_no=form.reg_no.data,
            dept = form.dept.data,
            events='',
            password=hashed_password,
            mobile=form.mobile.data,
            )
        db.session.add(user)
        db.session.commit()

        subject = 'Welcome to Apocalypse \'22'
        to = user.email
        body = f'''
        Reserve the dates 25, 26, 27 Nov 2022 for taking part in interesting events!!!
        Take a lot at the events {url_for('events', _external=True)}<br><br>

        Don't forget <b> Mr. & Ms. Electrocrat <b> is waiting for you !!!! <br><br>
        
        <a href="{url_for('events', _external=True)}">Register for events</a> <br><br><br>

        Regards,<br>
        Electronics Engineers Association
        '''
        send_mail(to, subject, body, format='html')
        flash(f'Account has been created for { form.name.data } ! You can now log in', 'success')
        return redirect(url_for('login'))

    return render_template('signup.html', title='Register', form=form, active_page='signup')


@app.route('/login', methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        flash('Already Logged In.', 'info')
        return redirect(url_for('dashboard'))

    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            flash('Logged In!', 'success')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    
    return render_template('login.html', title='Login', form=form, active_page='login')

@app.route('/logout')
@login_required
def logout():
    if current_user.is_authenticated:
        logout_user()
        flash('Successfully Logged Out!', 'success')

    return redirect(url_for('home'))

def send_reset_email(user):
    m = 5
    token = user.get_reset_token(m*60) #120 sec valid token
    subject = 'Password Reset Request'
    to = user.email
    body = f'''
    To reset Password, Click on the following link (expires in {m} mins)
    {url_for('reset_password', token=token, _external=True)}
    '''
    send_mail(to, subject, body)


@app.route('/forgot-password', methods=["GET", "POST"])
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = ResetRequestForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('Please check your mail for reset !', 'info')
        return redirect(url_for('login'))

    return render_template('password_reset.html', title='Forgot Password', form=form)

@app.route('/forgot-password/<token>', methods=["GET", "POST"])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    user = User.verify_reset_token(token)
    if not user:
        flash('Invalid request or Expired token !!!', 'warning')
        return redirect(url_for('forgot_password'))

    form = ResetPasswordForm()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash(f'Your password has been reset! ', 'success')
        return redirect(url_for('login'))

    return render_template('reset_password.html', title='Reset Password',form=form)


@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', title=current_user.name, events_dict=events_dict)

@app.route('/events')
def events():
    event_types = json.load(open('event_types.json'))
    return render_template('events.html', title='Events', active_page='events', event_types=event_types)


@app.route('/tech-events')
def tech_events():
    t = {}
    for i in events_dict:
        if events_dict[i]['category'] == 'tech':
            t.update({i:events_dict[i]})
    
    return render_template('events_list.html', title='Tech Events', active_page='events', events=t, header='Technical Events')

@app.route('/non-tech-events')
def non_tech_events():
    t = {}
    for i in events_dict:
        if events_dict[i]['category'] == 'non_tech':
            t.update({i:events_dict[i]})

    return render_template('events_list.html', title='Non Tech Events', active_page='events', events=t, header='Non Technical Events')


@app.route('/workshops')
def workshops():
    t = {}
    for i in events_dict:
        if events_dict[i]['category'] == 'workshop':
            t.update({i:events_dict[i]})
    
    return render_template('events_list.html', title='Workshops', active_page='events', events=t, header='Workshops')


@app.route('/event_details/<id>')
def event_details(id):
    # return render_template('event_details.html', event=events_dict[id], id=id)
    # print(result_dict[id]['winner'])
    winners = []
    runners = []
    try:
        for i in result_dict[id]['winner']:
            winners.append(User.query.filter_by(reg_no=i).first())
        
        for i in result_dict[id]['runner']:
            runners.append(User.query.filter_by(reg_no=i).first())

        return render_template('event_result.html', winners=winners, runners=runners, event=events_dict[id])

    except:
        #if no winner or runner defined, then don't do anything, in which case event details will be displayed 
        return render_template('event_details.html', event=events_dict[id], id=id)
    
    
@app.route('/register', methods=["POST"])
def register():
    data = dict(request.form)
    print(data)
    users = []
    try:
        for key, value in data.items():
            # if not value:
            #     continue
            if 'reg' not in key:
                continue
            try:
                x = User.query.filter_by(reg_no=value).first()
                if x:
                    # print('data', data['id'])
                    # print('events', x.events)
                    if data['id'] in x.events.split(','):
                        return jsonify({"error": f'{x.reg_no} Already registered!'})

                    users.append(x)
                else:
                    return jsonify({"error":f'{value} not registered !'})

            except Exception as e:
                return jsonify({"error":str(e)})

        r = ''
        users = set(users)
        for i in users:
            r+=(str(i.reg_no)+',')
            i.events += data['id']+','
        
        evt_reg = Events(
            event_id=data['id'],
            reg_no = r[:-1],
            time=str(datetime.now())
            )
        db.session.add(evt_reg)
        db.session.commit()

        p = evt_reg.reg_no.split(',')

        for i in users:
            subject = 'Registation Successful | Apocalypse 2k22'
            to = i.email
            body = f'''
            Successfully Registed for {events_dict[data['id']]['title']} !
            Team Members : {', '.join(p)}
            Regards,
            EEA
            '''
            if data[id] == 'title_event':
                body += 'Some other message specific to the event'
            send_mail(to, subject, body)
                
        return jsonify({"success":"registered!"})
    except Exception as e:
        return jsonify({"error":str(e)})


@app.route('/apocalyse/admin/see/data', methods=["GET", "POST"])
@login_required
def admin_login():
    form = AdminForm()

    if form.validate_on_submit():
        data = []
        if form.password.data == "adminpass":
            send_mail('admin@gmail.com', 'Admin Login Detected', f'Admin Logged In! --- {current_user.name, current_user.mobile, current_user.email}')
            users = User.query.all()
            evts = Events.query.order_by(Events.event_id).all()
            for i in evts:
                name = events_dict[i.event_id]['title']
                us = []
                for i in i.reg_no.split(','):
                    if i:
                        u = User.query.filter_by(reg_no=i).first()
                        us.append((u.name, u.reg_no, u.mobile, u.email))
                data.append((name, us))
            return render_template('data.html', data=data)
        else:
            flash("Wrong Password", "danger")    
    return render_template('admin_login.html', form=form)
    
@app.route('/refresh', methods=["POST"])
def refresh():
    req = dict(request.form)
    if req['request'] == 'refresh':
        data = []
        users = User.query.all()
        
        if req['event_id'] == 'all':
            evts = Events.query.order_by(Events.event_id).all()
        else:
            evts = Events.query.filter_by(event_id=req['event_id']).all()

        for i in evts:
            name = events_dict[i.event_id]['title']
            us = []
            for i in i.reg_no.split(','):
                if i:
                    u = User.query.filter_by(reg_no=i).first()
                    us.append((u.name, u.reg_no, u.mobile, u.email))
            data.append((name, us))
        return jsonify({"html":render_template('admin_data_content.html', data=data), "time":str(datetime.now())})
    return jsonify({"html":"error"})


# **************** Error Pages ****************

@app.errorhandler(404)
def page_not_found(e):
    return render_template('page_not_found.html')
@app.errorhandler(405)
def method_not_allowed(e):
    return render_template('method_not_allowed.html')

# ***********************************************

# ****************** Sending Mail via HTTP *******

from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
import base64

from email import encoders
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
import mimetypes

import os

def send_mail(to, subject, body, format='plain', attachments=[]):
    creds = None
    SCOPES = ['https://mail.google.com/']
    creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    service = build('gmail', 'v1', credentials=creds)

    file_attachments = attachments

    #create email
    mimeMessage = MIMEMultipart()
    mimeMessage['to'] = to
    mimeMessage['subject'] = subject
    #mimeMessage.attach(MIMEText(html,'html'))
    mimeMessage.attach(MIMEText(body, format))

    for attachment in file_attachments:
        content_type, encoding = mimetypes.guess_type(attachment)
        main_type, sub_type = content_type.split('/', 1)
        file_name = os.path.basename(attachment)

        with open(attachment, 'rb') as f:
            myFile = MIMEBase(main_type, sub_type)
            myFile.set_payload(f.read())
            myFile.add_header('Content-Disposition', attachment, filename=file_name)
            encoders.encode_base64(myFile)

        mimeMessage.attach(myFile)


    raw_string = base64.urlsafe_b64encode(mimeMessage.as_bytes()).decode()


    message = service.users().messages().send(
        userId='me',
        body={'raw': raw_string}).execute()

    return message


# ***********************************************

# ******** remove after testing / to check for working of the API***********
@app.route('/beta/send_message/<msg>/to/<id>')
def send(msg, id):
    message = send_mail(id, 'Hello(Beta)', msg)
    return message

# ****************************************
