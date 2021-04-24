from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import *

# Home page: shows all active listings.
def index(request):
    active = Auction.objects.filter(active=True)
    active=active.order_by("-date").all()
    return render(request, "auctions/index.html",{
        "listings": active,
        "view": 'ACTIVE LISTINGS'
    })

# Create a new listing
def create(request):
    # Make sure info came in via a POST request
    if request.method =='POST':
        # Extract info
        title = request.POST['title']
        description = request.POST['description']
        start_bid = request.POST['start_bid']
        category = request.POST['category']
        new_listing = Auction(title=title, description=description, start_bid=start_bid, max_bid=start_bid, category=category)
        new_listing.save()
        new_listing.image = request.FILES['image']
        new_listing.save()
        
        # Add this listing as part of the author's profile.
        author = User.objects.get(username=request.user) 
        author.created_listing.add(new_listing)
        author.save()

        # Show new listing
        return HttpResponseRedirect(reverse('listing', args=(new_listing.id,))) # Redirect to the listing view (index)
        
    # If the person just clicked on the link to create a new listing (GET request), bring them to the page
    return render(request, "auctions/create.html") 


# View for the individual listings
def listing(request, listing_id):
    listing_item = Auction.objects.get(pk=listing_id) # Current listing we're looking at
    curr_max_bid = listing_item.max_bid # Max bid stored in the listing model
    bids = Bid.objects.filter(item=listing_item) # Get all bids made on this listing
    listing_owner = listing_item.owner.first() # Get listing owner
    comments = Comment.objects.filter(item=listing_item) # Get listing comments
    comments = comments.order_by("-time").all() # Arrange comments in reverse order

    # POST METHOD
    if request.method=='POST':
        # Add the current listing to current user's watchlist.
        if request.POST['called_for']=='watchlist':
            current_user = User.objects.get(username=request.user)
            current_user.watchlist.add(listing_item)
            # Show message to indicate successful addition into watchlist
            return render(request, "auctions/listing.html", {
                "listing": listing_item,
                "no_of_bids": bids.count(),
                "comments": comments,
                "message": 'Item added to watchlist successfully !'
                })

        # Bid for the current listing
        if request.POST['called_for']=='bid':
            # The amount inputed into the bidding field on the page
            bid_amount = request.POST['bid_amount']
            # If this amount is less than the current max bid
            if int(bid_amount) <= int(curr_max_bid):
                # Return "Invalid Bid" error message
                bid_message = f"Invalid Bid: Please bid above £{curr_max_bid}."

            # Else, accept the bid
            else: 
                # Save bid into bid model.
                bidder = User.objects.get(username=request.user)
                new_bid = Bid (price=bid_amount, item=listing_item, user=bidder)
                new_bid.save() 
                # Replace max bid to the listing
                listing_item.max_bid = bid_amount
                listing_item.save()
                # Return success message    
                bid_message = f"Your bid has been accepted!"

            # Render view with message based on bid outcome
            return render(request, "auctions/listing.html", {
            "listing": listing_item,
            "no_of_bids": bids.count(),
            "bid_message": bid_message,
            "comments": comments
            })

        # Comment on the current listing 
        if request.POST['called_for']=='comments':
            # Add new comment into the comment model
            comment = request.POST['comment']
            commenter = User.objects.get(username=request.user)
            new_comment = Comment(content=comment, author=commenter, item= listing_item)
            new_comment.save() 

        # Close the listing
        if request.POST['called_for'] == 'CLOSE LISTING':
            listing_item.active = False # change active status
            listing_item.save()

    # ELSE (GET METHOD)
    # If the listing has been closed (aka not active),
    if not listing_item.active:
        # If bids have been made,
        if bids.count() >0:
            # Identify the bidder that gave the highest bid
            max_bidder = bids.last().user
            # If the current user is this highest bidder
            if str(request.user) == str(max_bidder):
                # Display success message to the user
                max_bid_message = f'Congratulations {max_bidder}, you have secured the bid for £{curr_max_bid}!'

            else: 
                # No success message
                max_bid_message = None
            
        # Else, if no bids have been made
        else:
            # Just display the page without any messages
            max_bid_message = None
        
        # Render view for a closed listing
        return render(request, "auctions/listing.html",{
                "listing": listing_item,
                "comments": comments,
                "max_bid_message": max_bid_message
                }) 

    # Else, if it's active
    else:
        return render(request, "auctions/listing.html",{
            "listing": listing_item,
            "no_of_bids": bids.count(),
            "comments": comments
            })

#View for the watchlist.
def watchlist(request):
    current_user= User.objects.get(username=request.user)

    # POST: Remove a listing from the watchlist.
    if request.method=='POST':
        item_id=request.POST['listing_id']
        item_to_remove = Auction.objects.get(pk=item_id)
        current_user.watchlist.remove(item_to_remove)
        watchlist = current_user.watchlist.all()
        watchlist = watchlist.order_by("-date").all()
        return render(request, "auctions/index.html",{
        "listings": watchlist,
        "view": 'WATCHLIST'
    })

    # GET: regularly accessing the watchlist      
    watchlist = current_user.watchlist.all()
    watchlist = watchlist.order_by("-date").all()
    return render(request, "auctions/index.html",{
        "listings": watchlist,
        "view": 'WATCHLIST'
    })

# Individual category page
def category(request, category):
    listings_in_category = Auction.objects.filter(category=category)
    listings_in_category = listings_in_category.order_by("-date").all()
    return render (request, 'auctions/index.html', {
        'view': category.upper(),
        'listings': listings_in_category
    })

def search(request):
    if request.method == 'POST':
        search = request.POST['search'].lower()
        results = []
        for listing in Auction.objects.all():
            title = listing.title.lower()
            if len(title.split(search))>1:
                results.append(listing)
        return render (request, 'auctions/index.html', {
            'view': 'SEARCH RESULTS',
            'listings': results
            })

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")
