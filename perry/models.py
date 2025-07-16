from django.db import models
from django.core.validators import FileExtensionValidator
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    is_celestial = models.BooleanField(
        default=False,
        help_text="Designates whether this user is a celestial object"
    )

    class Meta:
        ordering = ['username']

    def __str__(self):
        return self.username

class CelestialProfile(models.Model):
    CELESTIAL_TYPES = [
        ('planet', 'Planet'),
        ('star', 'Star'),
        ('galaxy', 'Galaxy'),
        ('black_hole', 'Black Hole'),
        ('comet', 'Comet'),
        ('dwarf_planet', 'Dwarf Planet'),
        ('moon', 'Moon'),
        ('asteroid', 'Asteroid'),
    ]

    name = models.CharField(max_length=100, unique=True)
    celestial_type = models.CharField(
        max_length=50,
        choices=CELESTIAL_TYPES,
        default='planet'
    )
    temperature = models.FloatField(
        help_text="Surface temperature in Kelvin"
    )
    has_rings = models.BooleanField(
        default=False,
        help_text="Does this celestial have rings?"
    )
    moon_count = models.IntegerField(
        default=0,
        help_text="Number of moons"
    )
    personality_prompt = models.TextField(
        help_text="LLM prompt for this celestial's personality"
    )
    base_response_delay = models.PositiveIntegerField(
        default=5,
        help_text="Base response delay in minutes"
    )
    gif = models.FileField(
        upload_to='celestial_gifs/',
        validators=[FileExtensionValidator(['gif'])],
        blank=True,
        null=True,
        help_text="Animated profile GIF"
    )
    image_url = models.URLField(
        blank=True,
        help_text="Fallback image URL if GIF not available"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.get_celestial_type_display()})"

    class Meta:
        ordering = ['name']
        verbose_name = "Celestial Profile"
        verbose_name_plural = "Celestial Profiles"

class Swipe(models.Model):
    LEFT = 'L'
    RIGHT = 'R'
    SWIPE_CHOICES = [
        (LEFT, 'Left'),
        (RIGHT, 'Right'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='swipes'
    )
    celestial = models.ForeignKey(
        CelestialProfile,
        on_delete=models.CASCADE,
        related_name='swipes_received'
    )
    direction = models.CharField(
        max_length=1,
        choices=SWIPE_CHOICES
    )
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [['user', 'celestial']]
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'celestial']),
            models.Index(fields=['timestamp']),
        ]

    def __str__(self):
        return f"{self.user} swiped {self.get_direction_display()} on {self.celestial}"

class Match(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='matches'
    )
    celestial = models.ForeignKey(
        CelestialProfile,
        on_delete=models.CASCADE,
        related_name='matches'
    )
    celestial_swiped_right = models.BooleanField(
        default=False,
        help_text="Did the celestial also swipe right?"
    )
    matched_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(
        default=True,
        help_text="Is this match still active?"
    )

    class Meta:
        unique_together = [['user', 'celestial']]
        ordering = ['-matched_at']
        verbose_name_plural = "Matches"

    def __str__(self):
        return f"Match between {self.user} and {self.celestial}"

    @property
    def is_mutual(self):
        return self.celestial_swiped_right

class ChatThread(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    celestial = models.ForeignKey(CelestialProfile, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ('user', 'celestial')
        ordering = ['-created_at']

    def __str__(self):
        return f"Chat with {self.celestial.name}"

class Message(models.Model):
    thread = models.ForeignKey(ChatThread, related_name='messages', on_delete=models.CASCADE)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)
    is_celestial = models.BooleanField(default=False)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        sender = "You" if not self.is_celestial else self.thread.celestial.name
        return f"{sender}: {self.content[:20]}..."