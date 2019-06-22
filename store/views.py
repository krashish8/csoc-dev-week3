from django.shortcuts import render
from django.shortcuts import get_object_or_404
from store.models import *
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpRequest
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime

# Create your views here.

def index(request):
    return render(request, 'store/index.html')

def bookDetailView(request, bid):
    template_name='store/book_detail.html'
    context={
        'book':None, # set this to an instance of the required book
        'num_available':None, # set this 1 if any copy of this book is available, otherwise 0
    }
    # START YOUR CODE HERE
    context['book'] = Book.objects.get(pk=bid)
    book_instance = BookCopy.objects.filter(book = context['book'], status=True)
    if book_instance:
        context['num_available'] = len(book_instance)
    else:
        context['num_available'] = 0
    
    return render(request,template_name, context=context)

@csrf_exempt
def bookListView(request):
    template_name='store/book_list.html'
    context={
        'books':None, # set here the list of required books upon filtering using the GET parameters
    }
    get_data=request.GET
    # START YOUR CODE HERE
    books = Book.objects.all()
    try:
        books = books.filter(title__icontains=get_data['title'])
    except:
        pass
    try:
        books = books.filter(author__icontains=get_data['author'])
    except:
        pass
    try:
        books = books.filter(genre__icontains=get_data['genre'])
    except:
        pass
    context['books'] = books

    # Rating System
    if request.user.is_authenticated:
        ratings = BookRating.objects.all()
        rating_dict = {}
        for book in context['books']:
            if BookRating.objects.filter(book=book.id, rated_by=request.user):
                rating_dict[book.id] = BookRating.objects.get(book=book.id, rated_by=request.user).rating
            else:
                rating_dict[book.id] = ''
        context['rating'] = rating_dict
    if request.method == "POST":
        bid = request.POST.get('bid')
        rating = request.POST.get('rating')
        try:
            book_rating = BookRating.objects.get(book=bid, rated_by=request.user)
            book_rating.rating = rating
            book_rating.save()
        except:
            BookRating.objects.create(book=Book.objects.get(pk=bid), rated_by=request.user, rating=rating)

    # Updating rating of book as average of rating by all users
    for book in context['books']:
        bookratings = BookRating.objects.filter(book=book.id)
        avg = 0
        c = 0
        if bookratings:
            for bookrating in bookratings:
                avg += bookrating.rating
                c += 1
            avg /= c
            Book.objects.filter(pk=book.id).update(rating=avg)
    return render(request,template_name, context=context)

@login_required
def viewLoanedBooks(request):
    template_name='store/loaned_books.html'
    context={
        'books':None,
    }
    '''
    The above key books in dictionary context should contain a list of instances of the 
    bookcopy model. Only those books should be included which have been loaned by the user.
    '''
    # START YOUR CODE HERE
    context['books'] = BookCopy.objects.filter(borrower=request.user)


    return render(request,template_name,context=context)

@csrf_exempt
@login_required
def loanBookView(request):
    response_data={
        'message':None,
    }
    '''
    Check if an instance of the asked book is available.
    If yes, then set message to 'success', otherwise 'failure'
    '''
    # START YOUR CODE HERE
    book_id = None # get the book id from post data
    book_id = request.POST['bid']
    book_instance = BookCopy.objects.filter(book=book_id, status=True).first()
    if book_instance:
        book_instance.borrow_date = datetime.today().strftime('%Y-%m-%d')
        book_instance.status = False
        book_instance.borrower = request.user
        book_instance.save()
        response_data['message'] = 1
    else:
        response_data['message'] = "failure"

    return JsonResponse(response_data)

'''
FILL IN THE BELOW VIEW BY YOURSELF.
This view will return the issued book.
You need to accept the book id as argument from a post request.
You additionally need to complete the returnBook function in the loaned_books.html file
to make this feature complete
''' 
@csrf_exempt
@login_required
def returnBookView(request):
    response_data={
        'message':None,
    }
    book_instance_id = request.POST.get('bid')
    book_instance = BookCopy.objects.get(id=book_instance_id)
    if book_instance:
        book_instance.borrow_date = None
        book_instance.status = True
        book_instance.borrower = None
        book_instance.save()
        response_data['message'] = 1
    else:
        response_data['message'] = "failure"

    return JsonResponse(response_data)

