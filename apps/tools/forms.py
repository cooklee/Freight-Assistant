from django import forms


class LeasingForm(forms.Form):
    vehicle_price = forms.IntegerField(
        widget=forms.TextInput(attrs={'class': 'input input-bordered w-full'})
    )
    initial_fee = forms.IntegerField(
        label='Initial Fee in % of vehicle price',
        initial=10,
        widget=forms.TextInput(attrs={'class': 'input input-bordered w-full'})
    )
    leasing_administration_fee = forms.IntegerField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'input input-bordered w-full'})
    )
    vehicle_registration_fee = forms.IntegerField(
        widget=forms.TextInput(attrs={'class': 'input input-bordered w-full'})
    )
    domestic_transport_license = forms.IntegerField(
        initial=880,
        widget=forms.TextInput(attrs={'class': 'input input-bordered w-full'})
    )
    eu_community_license = forms.IntegerField(
        required=False,
        initial=8000,
        widget=forms.TextInput(attrs={'class': 'input input-bordered w-full'})
    )
    leasing_installment = forms.IntegerField(
        widget=forms.TextInput(attrs={'class': 'input input-bordered w-full'})
    )
    insurance = forms.IntegerField(
        widget=forms.TextInput(attrs={'class': 'input input-bordered w-full'})
    )
    gap_insurance = forms.IntegerField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'input input-bordered w-full'})
    )
    security_installment = forms.IntegerField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'input input-bordered w-full'})
    )


class SalaryForm(forms.Form):
    brutto_salary = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        widget=forms.TextInput(attrs={'class': 'input input-bordered w-full'})
    )


class ProfitForm(forms.Form):
    tonne_kilometer_price = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        widget=forms.TextInput(attrs={'class': 'input input-bordered w-full'})
    )
    number_of_vehicles = forms.IntegerField(
        label='How many vehicles do you have?',
        widget=forms.TextInput(attrs={'class': 'input input-bordered w-full'})
    )
    vehicle_efficiency = forms.DecimalField(
        label='Vehicle efficiency - in tonne kilometers per day',
        max_digits=10,
        decimal_places=2,
        widget=forms.TextInput(attrs={'class': 'input input-bordered w-full'})
    )
    year_work_days = forms.IntegerField(
        widget=forms.TextInput(attrs={'class': 'input input-bordered w-full'})
    )
    leasing = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        widget=forms.TextInput(attrs={'class': 'input input-bordered w-full'})
    )
    fuel = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        widget=forms.TextInput(attrs={'class': 'input input-bordered w-full'})
    )
    salaries = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        widget=forms.TextInput(attrs={'class': 'input input-bordered w-full'})
    )
    taxes = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        widget=forms.TextInput(attrs={'class': 'input input-bordered w-full'})
    )
    invoices = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        widget=forms.TextInput(attrs={'class': 'input input-bordered w-full'})
    )
    other_expenses = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        widget=forms.TextInput(attrs={'class': 'input input-bordered w-full'})
    )
