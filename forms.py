from re import subn
from flask_wtf import FlaskForm
from wtforms import IntegerField, SubmitField, StringField
from wtforms.validators import DataRequired, Email

class get_stock_form(FlaskForm):
    load_books = IntegerField('Number of books', validators=[DataRequired()])
    submit = SubmitField('Submit')

class removeBook(FlaskForm):
    remove_book = IntegerField('Book Id', validators=[DataRequired()])
    submit = SubmitField('Submit')

class addMember(FlaskForm):
    member_name = StringField('Member Name', validators=[DataRequired()])
    member_email = StringField('Member Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Submit')

class removeMember(FlaskForm):
    member_email_remove = StringField('Member Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Submit')

class issueBook(FlaskForm):
    book_id = IntegerField('Book ID', validators=[DataRequired()])
    member_email_to_issue = StringField('Member Email', validators=[DataRequired()])
    submit = SubmitField('Submit')

class returnBook(FlaskForm):
    return_book_id = IntegerField('Book ID', validators=[DataRequired()])
    member_email_to_return = StringField('Member Email', validators=[DataRequired()])
    submit = SubmitField('Submit')

class searchBook(FlaskForm):
    book_name = StringField('Book Name', validators=[DataRequired()])
    author_name = StringField('Author Name', validators=[DataRequired()])
    submit = SubmitField('Submit')