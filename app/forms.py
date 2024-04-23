from flask_wtf import FlaskForm
from wtforms import SelectMultipleField, SubmitField, widgets, SelectMultipleField, StringField, PasswordField, \
    BooleanField, ValidationError, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, Length
from app.models import User


from app import cocktailRecommender


class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


class EvalForm(FlaskForm):
    opinions = ['Bad','Neutral', 'Good']
    op_list = [(x, x) for x in opinions]
    options = MultiCheckboxField('Label', choices=op_list)
    submit = SubmitField('Submit')


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()], render_kw={"placeholder": "username"})
    password = PasswordField('Password', validators=[DataRequired()],  render_kw={"placeholder": "password"})
    remember_me = BooleanField('Recuérdame')
    submit = SubmitField('Login')


class SimpleForm(FlaskForm):
    fruits, alco, nonalco, others = cocktailRecommender.get_general_taxonomy()
    
    fruits = sorted(fruits)
    alco = sorted(alco)
    nonalco = sorted(nonalco)
    others = sorted(others)

    
    fruit_list = [(x.title(), x.title()) for x in fruits if x != '']
    alco_list = [(x.title(), x.title()) for x in alco if x != '']
    nonalco_list = [(x.title(), x.title()) for x in nonalco if x != '']
    others_list = [(x.title(), x.title()) for x in others if x != '']

    fruits_cb = MultiCheckboxField('Label', choices=fruit_list)
    alco_cb = MultiCheckboxField('Label', choices=alco_list)
    nonalco_cb = MultiCheckboxField('Label', choices=nonalco_list)
    others_cb = MultiCheckboxField('Label', choices=others_list)

    style = {'type': 'button', 'class':'btn btn-primary'}
    submit = SubmitField('Search')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()], render_kw={"placeholder": "username"})
    email = StringField('Email', validators=[DataRequired(), Email()], render_kw={"placeholder": "email"})
    password = PasswordField('Password', validators=[DataRequired()], render_kw={"placeholder": "password"})
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')], render_kw={"placeholder": "password confirmation"})
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')


class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Request Password Reset')


class MessageForm(FlaskForm):
    message = TextAreaField(('Message'), validators=[DataRequired(), Length(min=0, max=140)])
    submit = SubmitField(('Submit'))