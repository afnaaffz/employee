from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from new_app.forms import EmployeeForm
from new_app.models import Employee

# Create your views here.

def index(request):
    return render(request,"index.html")
def employee_list(request):
    employees = Employee.objects.all()
    if request.method == 'POST':
        search_term = request.POST.get('search_term')
        if search_term:
            employees = employees.filter(
                Q(emp_id__iexact=search_term) |
                Q(emp_name__icontains=search_term)
            )
    return render(request, 'employee_list.html', {'employees': employees})

def employee_add(request):
    if request.method == 'POST':
        form = EmployeeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('employee_list')
    else:
        form = EmployeeForm()
    return render(request, 'employee_add.html', {'form': form})

def employee_search(request):
    if request.method == 'POST':
        search_term = request.POST.get('search_term')
        employees = Employee.objects.filter(
            Q(emp_id__iexact=search_term) |
            Q(emp_name__icontains=search_term)
        )
        return render(request, 'employee_list.html', {'employees': employees})
    return render(request, 'employee_search.html')


def employee_delete(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    if request.method == 'POST':
        employee.delete()
        return redirect('employee_list')
    return redirect('employee_list')