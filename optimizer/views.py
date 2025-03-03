from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import SupplyChainForm
from .models import Product
import pulp

# Login View
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'login.html')

# Signup View
def signup_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        if password1 == password2:
            if len(password1) >= 8:
                try:
                    user = User.objects.create_user(username=username, password=password1)
                    login(request, user)
                    return redirect('home')
                except:
                    messages.error(request, 'Username already exists.')
            else:
                messages.error(request, 'Password must be at least 8 characters long.')
        else:
            messages.error(request, 'Passwords do not match.')
    return render(request, 'signup.html')

# Logout View
def logout_view(request):
    logout(request)
    return redirect('login')

# Home View
@login_required
def home_view(request):
    return render(request, 'home.html')
# Login View


# Logout View
def logout_view(request):
    logout(request)
    return redirect('login')

# Home View
@login_required
def home_view(request):
    return render(request, 'home.html')

# Optimize View
@login_required
def optimize_view(request):
    if request.method == 'POST':
        form = SupplyChainForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            demand = form.cleaned_data['demand']
            supply = form.cleaned_data['supply']
            cost = form.cleaned_data['cost']

            # Linear Programming Problem
            prob = pulp.LpProblem("SupplyChainOptimization", pulp.LpMinimize)
            x = pulp.LpVariable('x', lowBound=0, cat='Continuous')
            prob += cost * x, "Total Cost"
            prob += x >= demand, "Demand Constraint"
            prob += x <= supply, "Supply Constraint"
            prob.solve()

            # Get results
            optimal_units = pulp.value(x)
            total_cost = pulp.value(prob.objective)

            # Save product to database
            product = Product(
                user=request.user,
                name=name,
                demand=demand,
                supply=supply,
                cost=cost
            )
            product.save()

            # Provide suggestions
            suggestion = ""
            if demand > supply:
                suggestion = f"Warning: Supply is less than demand for {name}. You need {demand - supply} more units."
            elif demand == supply:
                suggestion = f"Optimal: Supply meets demand for {name}."
            else:
                suggestion = f"Supply exceeds demand for {name}. You have {supply - demand} extra units."

            # Fetch all products for the user
            products = Product.objects.filter(user=request.user)

            # Calculate differences for each product
            product_data = []
            for product in products:
                difference = product.demand - product.supply
                absolute_difference = abs(difference)
                product_data.append({
                    'id': product.id,
                    'name': product.name,
                    'demand': product.demand,
                    'supply': product.supply,
                    'cost': product.cost,
                    'difference': difference,
                    'absolute_difference': absolute_difference
                })

            return render(request, 'optimize.html', {
                'form': form,
                'result': f"Optimal Units: {optimal_units}, Total Cost: {total_cost}",
                'suggestion': suggestion,
                'products': product_data
            })
    else:
        form = SupplyChainForm()
        products = Product.objects.filter(user=request.user)

        # Calculate differences for each product
        product_data = []
        for product in products:
            difference = product.demand - product.supply
            absolute_difference = abs(difference)
            product_data.append({
                'id': product.id,
                'name': product.name,
                'demand': product.demand,
                'supply': product.supply,
                'cost': product.cost,
                'difference': difference,
                'absolute_difference': absolute_difference
            })

    return render(request, 'optimize.html', {'form': form, 'products': product_data})

@login_required
def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id, user=request.user)
    if request.method == 'POST':
        product.delete()
    return redirect('optimize')

@login_required
def update_product(request, product_id):
    product = get_object_or_404(Product, id=product_id, user=request.user)
    if request.method == 'POST':
        form = SupplyChainForm(request.POST)
        if form.is_valid():
            product.name = form.cleaned_data['name']
            product.demand = form.cleaned_data['demand']
            product.supply = form.cleaned_data['supply']
            product.cost = form.cleaned_data['cost']
            product.save()
            return redirect('optimize')
    else:
        form = SupplyChainForm(initial={
            'name': product.name,
            'demand': product.demand,
            'supply': product.supply,
            'cost': product.cost
        })
    return render(request, 'update_product.html', {'form': form})