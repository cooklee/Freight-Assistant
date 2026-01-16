from django import forms


class LeasingForm(forms.Form):
    vehicle_price = forms.IntegerField(
        widget=forms.TextInput(attrs={'class': 'input input-bordered w-full'})
    )
    # TODO (finance): Dla kwot pieniężnych lepiej używać DecimalField niż IntegerField (cents/ grosze, VAT, zaokrąglenia).
    # TODO (ux): Rozważ widget NumberInput zamiast TextInput (łatwiejsze wpisywanie, walidacja w przeglądarce).

    initial_fee = forms.IntegerField(
        label='Initial Fee in % of vehicle price',
        initial=10,
        widget=forms.TextInput(attrs={'class': 'input input-bordered w-full'})
    )
    # TODO (validation): Dodaj MinValueValidator/MaxValueValidator (0-100) lub clean_initial_fee.
    # TODO (ux): To pole jest procentem, więc NumberInput + min/max byłby czytelniejszy.

    leasing_administration_fee = forms.IntegerField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'input input-bordered w-full'})
    )
    # TODO (finance): Jak wyżej — raczej DecimalField.
    # TODO (validation): Dla kosztów dodaj min_value=0, żeby nie dało się wprowadzić ujemnych opłat.

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
    # TODO (ux): required=False + initial=8000 bywa mylące: użytkownik widzi 8000, ale pole nadal "opcjonalne".
    # TODO (ux): Zastanów się czy to ma być domyślny koszt (wtedy required=True) albo naprawdę opcjonalne (wtedy initial=None/0).

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
    # TODO (finance): Wszystkie koszty miesięczne/kwoty → rozważ DecimalField + min_value=0.
    # TODO (style): Masz dużo powtórzeń widget attrs. Warto zrobić stałą CSS_CLASS.


class SalaryForm(forms.Form):
    brutto_salary = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        widget=forms.TextInput(attrs={'class': 'input input-bordered w-full'})
    )
    # TODO (validation): Dodaj min_value=0.
    # TODO (ux): Rozważ NumberInput (type="number") z step="0.01".


class ProfitForm(forms.Form):
    tonne_kilometer_price = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        widget=forms.TextInput(attrs={'class': 'input input-bordered w-full'})
    )
    # TODO (validation): min_value=0, bo cena ujemna raczej nie ma sensu.

    number_of_vehicles = forms.IntegerField(
        label='How many vehicles do you have?',
        widget=forms.TextInput(attrs={'class': 'input input-bordered w-full'})
    )
    # TODO (validation): min_value=0 lub min_value=1 (zależnie od logiki).

    vehicle_efficiency = forms.DecimalField(
        label='Vehicle efficiency - in tonne kilometers per day',
        max_digits=10,
        decimal_places=2,
        widget=forms.TextInput(attrs={'class': 'input input-bordered w-full'})
    )
    # TODO (validation): min_value=0.

    year_work_days = forms.IntegerField(
        widget=forms.TextInput(attrs={'class': 'input input-bordered w-full'})
    )
    # TODO (validation): min_value=0 i max_value=366 (albo 365) – zależnie od interpretacji.

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
    # TODO (validation): Dla wszystkich kosztów: min_value=0.
    # TODO (ux): required=False pola zwrócą None w cleaned_data — upewnij się, że kalkulacje traktują None jako 0 (Decimal("0")).
    # TODO (style): Jak wyżej — warto zredukować duplikację widgetów przez __init__ i pętlę po fields.
