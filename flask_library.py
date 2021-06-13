from flask import Flask, render_template, flash
from forms import get_stock_form, removeBook, addMember, removeMember, issueBook, returnBook, searchBook
import requests, json, MySQLdb
from random import randint
app = Flask(__name__)

app.config['SECRET_KEY'] = ''

@app.route("/")
def landing():
    return render_template('landing.html')

@app.route("/home", methods=['GET', 'POST'])
def home():

    #connect to database
    db = MySQLdb.connect(host="sql6.freesqldatabase.com",
                     user="sql6418117",
                     passwd="",
                     db="sql6418117")
    cur = db.cursor()
    print(db)
    
    #forms
    load_books = get_stock_form()
    remove_books = removeBook()
    add_member = addMember()
    remove_member = removeMember()

    #loading books into database
    if load_books.load_books.data != None:
        if load_books.load_books.data <= 0:
            flash(f'Cannot add {load_books.load_books.data} books!', 'danger')
        else:        
            number_of_books = load_books.load_books.data

            #calculating the number of times the loop will run to get books from api
            if number_of_books%20 != 0:
                loop_range = int(number_of_books/20) + 1
            else:
                loop_range = int(number_of_books/20)

            #getting data from api
            totalBooks = []
            for x in range(1,loop_range+1):
                page = requests.get(f"https://frappe.io/api/method/frappe-library?page={randint(1,200)}")
                content = page.content
                json_data = json.loads(content)
                data = json_data['message']
                if data != []:
                    for x in data:
                        totalBooks.append(x)
            
            #getting the actual number of books from totalBooks
            books = []
            for x in range(0,number_of_books):
                books.append(totalBooks[x])
            
            #formatting data and adding it to sql database
            for x in books:
                item = list(x.values())
                items = [x.encode('utf-8') for x in item]
                #sql query to add books
                cur.execute("insert into books (book_id, title, author, rating, isbn, isbn3, language, pages, rating_count, text_reviews, publication_date, publisher) values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", items)
            db.commit()

            if load_books.validate_on_submit():
                flash(f'{load_books.load_books.data} - books Added!', 'success')
    #########################################################################
            
    #removing a book from database
    if remove_books.remove_book.data != None:
        if remove_books.remove_book.data < 0:
            flash(f'Invalid Book ID', 'danger')
        else:
            book_id = str(remove_books.remove_book.data)
            #sql query to get id from books with book_id where issued = 0
            cur.execute("select id from books where book_id = %s AND issued = 0", [book_id])
            ids = cur.fetchone()
            if ids == None:
                flash(f'Cannot remove book! | Check Book ID or Book is issued', 'danger')
            else:
                id = list(ids)
                id = int(id[0])
                cur.execute('delete from books where id = %s', [id])
                flash(f'{remove_books.remove_book.data} - Book removed Successfully!', 'success')
                db.commit()
    #########################################################################

    #adding a member
    if add_member.member_name.data and add_member.member_name.data != "":
        name = add_member.member_name.data
        email = add_member.member_email.data
        #sql query to check if email already exists in members table
        cur.execute('select member_id from members where email = %s', [email])
        temp_mail = cur.fetchone()
        
        if temp_mail == None:
            item = [name, email]
            #adding member if email is not in members table
            cur.execute("insert into members(name, email) values(%s, %s)", item)
            db.commit()
            flash(f'{add_member.member_name.data} - member added Successfully!', 'success')
        else:
             flash(f'{add_member.member_email.data} - member already exists', 'danger')
    #########################################################################

    #removing a member
    if remove_member.member_email_remove.data != None and "":
        email_remove = remove_member.member_email_remove.data
        #sql query to check if email exists in members table
        cur.execute("select member_id from members where email = %s", [email_remove])
        temp_mail = cur.fetchone()
        if temp_mail != None:
            #removing member if email is in members table
            cur.execute("delete from members where email = %s", [email_remove])
            db.commit()
            flash(f'{remove_member.member_email_remove.data} - member removed Successfully!', 'success')
        else:
            flash(f'{remove_member.member_email_remove.data} - no such member', 'danger')
    ##########################################################################

    return render_template('home.html', form=load_books, form2=remove_books, form3=add_member, form4=remove_member)

@app.route("/guest")
def guest():
    db = MySQLdb.connect(host="sql6.freesqldatabase.com",
                     user="sql6418117",
                     passwd="",
                     db="sql6418117",
                     charset='utf8')
    cur = db.cursor()
    print(db)

    cur.execute("select * from books")
    temp = cur.fetchall()
    books = []
    for x in temp:
        books.append(list(x))
    headers = ['id','book_id','title','author','rating','isbn','isbn3','language','pages','rating_count','text_reviews','publication_date','publisher','issued']

    return render_template('guest.html',headers=headers, values=books)

@app.route("/issue", methods=['GET', 'POST'])
def issue():
    #connect to database
    db = MySQLdb.connect(host="sql6.freesqldatabase.com",
                     user="sql6418117",
                     passwd="",
                     db="sql6418117")
    cur = db.cursor()
    print(db)

    #forms
    issue_book = issueBook()
    return_book = returnBook()
    search_book = searchBook()

    #issue a book
    if (issue_book.book_id.data and issue_book.member_email_to_issue.data != None) and (issue_book.book_id.data and issue_book.member_email_to_issue.data != ""):
        book_id =  issue_book.book_id.data
        member_email = issue_book.member_email_to_issue.data
        #sql to check if book exists in the books table
        cur.execute("select id from books where book_id = %s AND issued = 0", [book_id])
        ids = cur.fetchone()
        if ids != None:
            id = list(ids)
            id = int(id[0])
            #sql to check if member exists in members table
            cur.execute('select member_id from members where email = %s', [member_email])
            member_id = cur.fetchone()
            if member_id != None: 
                #sql to issue book
                #get existing debt and books issued
                debt = cur.execute("select debt from members where member_id = %s", [member_id])
                debt = cur.fetchone()
                debt = list(debt)
                if debt == [None]:
                    debt = 100
                else:
                    if debt != [500]:
                        debt = debt[0] + 100
                        book_issue = cur.execute("select books_issued from members where member_id = %s", [member_id])
                        book_issue = cur.fetchall()
                        books = []
                        books_str = ""
                        if book_issue != ():
                            for x in book_issue:
                                books.append(books_str.join(list(x)))
                                books_str = ""
                            books.append(str(book_id))
                            books = ','.join(books)
                        else:
                            books = [str(book_id)]
                        item_debt = [debt, member_email]
                        item_books = [books, member_email]
                        #sql to update data for issuing book
                        cur.execute("update books set issued = 1 where id = %s", [id])
                        cur.execute('update members set debt = %s where email = %s', item_debt)
                        cur.execute('update members set books_issued = %s where email = %s', item_books)
                        db.commit()
                        flash(f'{issue_book.book_id.data} - book issued to - {issue_book.member_email_to_issue.data}', 'success')
                    else:
                       flash(f'{issue_book.member_email_to_issue.data} - debt is 500', 'danger') 
            else:
                flash(f'{issue_book.member_email_to_issue.data} - no such member', 'danger')
        else:
            flash(f'{issue_book.book_id.data} - book does not exist or it is issued', 'danger')
    ##########################################################################

    #return a book
    if (return_book.return_book_id.data and return_book.member_email_to_return.data != None) and (return_book.return_book_id.data and return_book.member_email_to_return.data != ""):
        book_id = return_book.return_book_id.data
        member_email = return_book.member_email_to_return.data
        
        #check if member exists
        cur.execute("select member_id from members where email = %s", [member_email])
        member_id = cur.fetchone()
        if member_id != None:
            #member exists
            #now check if there is a book issued to this member with the given book id
            books = []
            cur.execute("select books_issued from members where member_id = %s", [member_id])
            book = cur.fetchall()
            if book != ((None,),):
                for x in book:
                    books = list(x)
                for x in books:
                    books = x.split(",")
                if str(book_id) in books:
                    #book is issued to member now to return it and charge money and reduce debt
                    books.remove(str(book_id))
                    books = ",".join(books)
                    item = [books, member_email]
                    #update books issued
                    cur.execute("update members set books_issued = %s where email = %s", item)
                    cur.execute("select debt from members where member_id = %s", [member_id])
                    debt = cur.fetchone()
                    debt = list(debt)
                    debt = debt[0] - 100
                    item = [debt, member_email]
                    #update debt
                    cur.execute("update members set debt = %s where email = %s", item)
                    cur.execute("select id from books where book_id = %s AND issued = 1", [str(book_id)])
                    id = cur.fetchone()
                    #updating issued in books
                    cur.execute("update books set issued = 0 where id = %s", id)
                    #adding transaction
                    item = [member_email, 100]
                    cur.execute("insert into transactions (member, amount) values (%s, %s)", item)
                    db.commit()
                    flash(f'{return_book.return_book_id.data} - book returned from - {return_book.member_email_to_return.data}', 'success')
                else:
                    flash(f'{return_book.return_book_id.data} - no such book issued to - {return_book.member_email_to_return.data}', 'danger')
            else:
                flash(f'{return_book.return_book_id.data} - no such book issued to - {return_book.member_email_to_return.data}', 'danger')
        else:
            flash(f'No such member - {return_book.member_email_to_return.data}', 'danger')
    ##########################################################################

    #search book
    if (search_book.book_name.data and search_book.author_name.data != None) and (search_book.book_name.data and search_book.author_name.data != ""):
        book_name = search_book.book_name.data
        author_name = search_book.author_name.data
        book_name = book_name.encode('utf-8')
        author_name = author_name.encode('utf-8')
        #searching for the book
        item = [book_name, author_name]
        cur.execute("select id from books where title = %s AND author = %s", item)
        ids = cur.fetchall()
        id = []
        if ids != ():
            for x in ids:
                id.append(list(x))
            flash(f"The id's of books with name - {book_name} and author - {author_name} are: {id}", 'success')
        else:
            flash(f"No such book available - book: {book_name}, author: {author_name}", 'danger')
    ##########################################################################

    return render_template('issue.html', form=issue_book, form2=return_book, form3=search_book)

@app.route("/report1")
def report1():
    #connect to database
    db = MySQLdb.connect(host="sql6.freesqldatabase.com",
                     user="sql6418117",
                     passwd="",
                     db="sql6418117",
                     charset='utf8')
    cur = db.cursor()
    print(db)

    cur.execute("select * from books")
    temp = cur.fetchall()
    raw_data = []
    for x in temp:
        raw_data.append(list(x))
    total_number_of_books = len(raw_data)
    data_quantity = {}
    data_popularity = {}
    
    for x in raw_data:
        item = x
        book = item[2]
        issued = item[-1]
        if book not in data_popularity.keys():
            data_popularity[book] = issued
            data_quantity[book] = 1
        else:
            data_popularity[book] += issued
            data_quantity[book] += 1
    
    books = list(data_quantity.keys())
    quantity = list(data_quantity.values())
    popularity = list(data_popularity.values())

    return render_template('report1.html', books=books, quantity=quantity, total=total_number_of_books)

@app.route("/report2")
def report2():
    #connect to database
    db = MySQLdb.connect(host="sql6.freesqldatabase.com",
                     user="sql6418117",
                     passwd="",
                     db="sql6418117")
    cur = db.cursor()
    print(db)

    cur.execute("select * from transactions")
    temp = cur.fetchall()
    raw_data = []
    for x in temp:
        raw_data.append(list(x))
    
    data = {}
    for x in raw_data:
        item = x
        member = item[1]
        amount = item[2]
        if member not in data.keys():
            data[member] = amount
        else:
            data[member] += amount
    
    members = list(data.keys())
    amount = list(data.values())

    return render_template('report2.html', members = members, amount = amount)

if __name__ == '__main__':
    app.run(debug=True)