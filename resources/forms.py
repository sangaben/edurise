from django import forms
from .models import UploadedContent

class UploadedContentForm(forms.ModelForm):
    class Meta:
        model = UploadedContent
        fields = ['title', 'description', 'content_type', 'file', 'youtube_url', 'cover_image']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'youtube_url': forms.URLInput(attrs={'placeholder': 'https://www.youtube.com/watch?v=...'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        content_type = cleaned_data.get('content_type')
        file = cleaned_data.get('file')
        youtube_url = cleaned_data.get('youtube_url')
        
        if content_type == 'youtube' and not youtube_url:
            raise forms.ValidationError("YouTube URL is required for YouTube content type.")
        elif content_type != 'youtube' and not file:
            raise forms.ValidationError("File is required for non-YouTube content types.")
        
        return cleaned_data