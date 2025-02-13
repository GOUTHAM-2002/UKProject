from django.db import models

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


class CustomUserManager(BaseUserManager):
    def create_user(self, email, phone_number, company_name, legal_name, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        if not phone_number:
            raise ValueError('Phone number is required')
        email = self.normalize_email(email)
        user = self.model(email=email, phone_number=phone_number, company_name=company_name, legal_name=legal_name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, phone_number, company_name, legal_name, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, phone_number, company_name, legal_name, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15)
    company_name = models.CharField(max_length=255)
    legal_name = models.CharField(max_length=255)
    profile_pic = models.ImageField(upload_to='profile_pics/', default='default_pic.jpg')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    # Add these related_name parameters to fix the conflict
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_set',
        blank=True,
        verbose_name='groups',
        help_text='The groups this user belongs to.',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_set',
        blank=True,
        verbose_name='user permissions',
        help_text='Specific permissions for this user.',
    )

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['phone_number', 'company_name', 'legal_name']

    def __str__(self):
        return self.email

class Therapist(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    years_of_experience = models.PositiveIntegerField()
    expertise = models.TextField()
    license_certificate = models.FileField(upload_to='certificates/')




class Ping(models.Model):
    therapist = models.ForeignKey(Therapist, on_delete=models.CASCADE, related_name='pings')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='pinged_therapists')
    timestamp = models.DateTimeField(auto_now_add=True)
    message = models.TextField(blank=True, null=True)
    last_message = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('therapist', 'user')



class Question(models.Model):
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text

class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    text = models.TextField()
    is_choice = models.BooleanField(default=True)  # To identify answer choices

    def __str__(self):
        return f"Answer to '{self.question.text}': {self.text[:50]}..."  # Display part of the answer

class Questionnaire(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='questionnaires')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE)
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Questionnaire for {self.user.email} - {self.question.text[:50]}"

class ChatMessage(models.Model):
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='chat_sent_messages')
    receiver = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='chat_received_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"{self.sender} to {self.receiver}: {self.content[:50]}"

class Message(models.Model):
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='system_sent_messages')
    receiver = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='system_received_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']

class Post(models.Model):
    POST_TYPES = (
        ('image', 'Image'),
        ('video', 'Video'),
        ('article', 'Article')
    )

    title = models.CharField(max_length=200)
    content = models.TextField()
    post_type = models.CharField(max_length=7, choices=POST_TYPES)
    media_file = models.FileField(upload_to='posts/', blank=True, null=True)
    thumbnail = models.ImageField(upload_to='post_thumbnails/', blank=True, null=True)
    author = models.ForeignKey('Therapist', on_delete=models.CASCADE, related_name='posts')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    upvotes = models.ManyToManyField(CustomUser, related_name='upvoted_posts', blank=True)
    upvote_count = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def update_upvote_count(self):
        self.upvote_count = self.upvotes.count()
        self.save()

