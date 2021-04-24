from django.contrib.auth.models import AbstractUser
from django.db import models
import os

def rename(instance,filename):
    filename = f'{instance.id}'
    return filename

#Auction Listings
class Auction(models.Model):
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=300)
    start_bid = models.FloatField()
    active = models.BooleanField(default=True)
    max_bid = models.IntegerField(blank=True)
    category = models.CharField(max_length=100)
    image = models.ImageField(upload_to=rename, blank=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.title}: £{self.max_bid}'

class User(AbstractUser):
    watchlist = models.ManyToManyField(Auction, blank=True, related_name='interested')
    created_listing = models.ManyToManyField(Auction, blank=True, related_name='owner')

#Bids
class Bid(models.Model):
    price = models.IntegerField()
    item = models.ForeignKey(Auction,on_delete=models.CASCADE, related_name='bid_item')
    user = models.ForeignKey(User,on_delete=models.CASCADE, related_name='bidder')

#Comments (on Auction Listings)
class Comment(models.Model):
    content = models.CharField(max_length=1000)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='commenter')
    item = models.ForeignKey(Auction, on_delete=models.CASCADE, related_name='comment_item')
    time = models.DateTimeField(auto_now_add=True)


    







