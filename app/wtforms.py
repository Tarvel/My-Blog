from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, TextAreaField, FileField
from wtforms.validators import DataRequired, Email



class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()], render_kw={"placeholder":"Email"})
    password = PasswordField('Password', render_kw={"placeholder":"Password"})
    submit = SubmitField('Login')


class PostForm(FlaskForm):
    post_image = FileField('Image for Post')
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content')
    tags = StringField('Tags: ', validators=[DataRequired()])
    submit = SubmitField('Publish')