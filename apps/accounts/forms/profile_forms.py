from django import forms

from apps.accounts.models import UserProfile


class UserProfileForm(forms.ModelForm):
    first_name = forms.CharField(label='Name', max_length=120)
    last_name = forms.CharField(label='Surname', max_length=120)
    twitter = forms.URLField(assume_scheme='https')
    facebook = forms.URLField(assume_scheme='https')
    instagram = forms.URLField(assume_scheme='https')
    linkedin = forms.URLField(assume_scheme='https')

    class Meta:
        model = UserProfile
        fields = [
            'profile_image', 'first_name', 'last_name', 'about_me',
            'job', 'country', 'address',
            'phone', 'twitter', 'facebook', 'instagram', 'linkedin'
        ]
        widgets = {
            'profile_image': forms.FileInput(attrs={
                'id': 'fileInput',
                'class': 'hidden',
            })
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if user:
            self.fields['first_name'].initial = user.first_name
            self.fields['last_name'].initial = user.last_name

        for field in self.fields.values():
            if not isinstance(field.widget, forms.FileInput):
                field.widget.attrs.update({'class': 'input input-bordered w-full'})
