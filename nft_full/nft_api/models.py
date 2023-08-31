from django.db import models

class NFT(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    author = models.CharField(max_length=50)
    image = models.ImageField(upload_to='nft_images/')

    def __str__(self):
        return self.title
