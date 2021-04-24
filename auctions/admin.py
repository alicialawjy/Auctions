from django.contrib import admin
from django.contrib import admin
from .models import Auction, Bid, User, Comment

class AuctionAdmin (admin.ModelAdmin):
    list_display = ('id','title','description','start_bid','image','category')

class BidAdmin (admin.ModelAdmin):
    list_display = ('id','price', 'item','user')

class CommentAdmin (admin.ModelAdmin):
    list_display = ('id','content','author','item')    

class UserAdmin (admin.ModelAdmin):
    list_displat = ('id', 'username','watchlist','created_listing')

# Register your models here.
admin.site.register(Auction, AuctionAdmin)
admin.site.register(User, UserAdmin)
admin.site.register(Bid,BidAdmin)
admin.site.register(Comment, CommentAdmin)