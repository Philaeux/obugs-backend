from django.db import models


class User(models.Model):
    id = models.IntegerField(primary_key=True)
    username = models.CharField(unique=True, max_length=255)


class Software(models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    fullname = models.CharField(max_length=255)
    editor = models.CharField(max_length=255)


class Tag(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255)
    software = models.ForeignKey(Software, on_delete=models.CASCADE)


class Bug(models.Model):
    id = models.IntegerField(primary_key=True)
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    software = models.ForeignKey(Software, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    status = models.CharField(max_length=50, default="NEW")
    rating_total = models.IntegerField(default=2)
    rating_count = models.IntegerField(default=1)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()


class BugVote(models.Model):
    id = models.IntegerField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    bug = models.ForeignKey(Bug, on_delete=models.CASCADE)
    rating = models.IntegerField(default=2)


class BugComment(models.Model):
    id = models.IntegerField(primary_key=True)
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    bug = models.ForeignKey(Bug, on_delete=models.CASCADE)
    comment = models.TextField()
    created_at = models.DateTimeField()


class Petition(models.Model):
    id = models.IntegerField(primary_key=True)
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    bug = models.ForeignKey(Bug, on_delete=models.CASCADE)
    field = models.CharField(max_length=50, default="title")
    value = models.TextField()
    rating = models.IntegerField(default=1)
    rating_count = models.IntegerField(default=1)
    created_at = models.DateTimeField()
    closed_at = models.DateTimeField()


class BugPetitionVotes(models.Model):
    id = models.IntegerField(primary_key=True)
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    petition = models.ForeignKey(Petition, on_delete=models.CASCADE)
    rating = models.IntegerField(default=1)
